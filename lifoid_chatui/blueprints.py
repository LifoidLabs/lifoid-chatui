# -*- coding: utf8 -*-
"""
Flask server application for Lifoid Web Chat UI
"""
import os
import base64
import boto3
import json
from contextlib import closing
from flask import (Blueprint, render_template, request, abort,
                   redirect, url_for, jsonify, make_response)
from flask import current_app as app
from flask_babel import refresh
from babel.core import UnknownLocaleError
from loggingmixin import ServiceLogger
from google.cloud import speech as google_speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account
from lifoid.config import settings
from lifoid.bot import get_bot
from lifoid.auth import get_user

logger = ServiceLogger()
CHATUI_PATH = os.path.abspath(os.path.dirname(__file__))
logger.debug('Static path: {}'.format(os.path.join(CHATUI_PATH, 'static')))
chatui = Blueprint('chatui', __name__, url_prefix='/chatui',
                   template_folder='templates',
                   static_folder='static')
speech = Blueprint('speech', __name__, url_prefix='/speech')


def get_lang(bot_conf):
    supported_languages = bot_conf['languages']
    lang = request.accept_languages.best_match(supported_languages)
    logger.debug('Best language found {}'.format(lang))
    if lang is None:
        return bot_conf['language']
    return lang


@chatui.route('/')
def root():
    """
    Delivers Lifoid web Chat UI.
    """
    default_chatbot_id = settings.lifoid_id
    bot_conf = get_bot(default_chatbot_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    lang = get_lang(bot_conf)
    return redirect(url_for('chatui.chatbot_lang',
                            chatbot_id=default_chatbot_id, lang_code=lang))


@chatui.route('/<lang_code>')
def root_lang(lang_code):
    """
    Website root
    """
    return chatbot_lang(settings.lifoid_id, lang_code)


@chatui.route('/chatbot/<chatbot_id>')
def chatbot(chatbot_id):
    bot_conf = get_bot(chatbot_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    lang = get_lang(bot_conf)
    return redirect(url_for('chatui.chatbot_lang',
                            chatbot_id=chatbot_id, lang_code=lang))


@chatui.route('/chatbot/<chatbot_id>/lang/<lang_code>')
def chatbot_lang(chatbot_id, lang_code):
    """
    Website root
    """
    logger.debug('Blueprint index invoked')
    app.config['BABEL_DEFAULT_LOCALE'] = lang_code.replace('-', '_')
    refresh()
    cognito_auth = True
    bot_conf = get_bot(chatbot_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    if settings.dev_auth == 'yes':
        cognito_auth = False
    try:
        return render_template(
            'index.html',
            color=bot_conf['chatui']['color'],
            color_active=bot_conf['chatui']['color_active'],
            lang=lang_code,
            path_url=settings.chatui.path_url,
            auth=cognito_auth,
            company_name=bot_conf['chatui']['company_name'],
            lifoid_id=chatbot_id,
            lifoid_name=bot_conf['chatui']['service_name'],
            cognito_clientid=bot_conf['auth']['client_id'],
            cognito_appwebdomain=bot_conf['auth']['web_domain'],
            cognito_redirecturisignin=bot_conf['auth']['url_signin'],
            cognito_redirecturisignout=bot_conf['auth']['url_signout'],
        )
    except UnknownLocaleError:
        return make_response('Not supported locale', 404)


@chatui.route('/expired/<chatbot_id>/lang/<lang_code>')
def expired(chatbot_id, lang_code):
    """
    Authenticated session has expired
    """
    bot_conf = get_bot(chatbot_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    return render_template(
        'expired.html',
        lifoid_name=bot_conf['chatui']['service_name'],
        lang=lang_code,
        lifoid_id=chatbot_id,
        cognito_clientid=bot_conf['auth']['client_id'],
        cognito_appwebdomain=bot_conf['auth']['web_domain'],
        cognito_redirecturisignin=bot_conf['auth']['url_signin'],
        cognito_redirecturisignout=bot_conf['auth']['url_signout']
    )


@chatui.route('/terms/<chatbot_id>/lang/<lang_code>')
def terms(chatbot_id, lang_code):
    """
    Terms of Use
    """
    bot_conf = get_bot(chatbot_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    return render_template(
        'terms.html',
        lifoid_name=bot_conf['chatui']['service_name'],
        lang=lang_code,
        lifoid_id=chatbot_id,
    )


@chatui.route('/privacy/<chatbot_id>/lang/<lang_code>')
def privacy(chatbot_id, lang_code):
    """
    Privacy Policy
    """
    return render_template(
        'privacy.html',
        lang=lang_code,
        lifoid_id=chatbot_id,
    )


@speech.route("/chatbot/<chatbot_id>/lang/<lang_code>/tts", methods=["POST"])
def synthesis(chatbot_id, lang_code):
    data = json.loads(request.get_data())
    user = get_user(data)
    if user is None:
        abort(403)
    text = data['q']['text']
    voice = request.form.get('voice', settings.chatui.voice)
    bot_conf = get_bot(chatbot_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    # For each block, invoke Polly API, which will transform text into audio
    voice = bot_conf['voice'].get(lang_code, None)
    if voice is None:
        return make_response('This language is not supported', 404)
    polly = boto3.client('polly')
    response = polly.synthesize_speech(
        OutputFormat='mp3',
        Text=text,
        VoiceId=voice
    )
    # Save the audio stream returned by Amazon Polly on Lambda's temp
    # directory. If there are multiple text blocks, the audio stream
    # will be combined into a single file.
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            resp = {}
            buff = stream.read()
            resp['audio'] = base64.b64encode(buff).decode("UTF-8")
            return jsonify(resp)
    else:
        return make_response('OK', 200)


@speech.route("/chatbot/<chatbot_id>/lang/<lang_code>/stt", methods=["POST"])
def reco(chatbot_id, lang_code):
    if 'data' not in request.form:
        abort(404)
    data = json.loads(request.form['data'])
    user = get_user(data)
    if user is None:
        abort(403)
    audio = request.files["file"].read()
    bot_conf = get_bot(chatbot_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    GOOGLE_CREDENTIALS = {
        "private_key_id": settings.chatui.google_speech_id,
        "private_key": settings.chatui.google_speech_key,
        "client_email": settings.chatui.google_speech_email,
        "token_uri": settings.chatui.google_speech_token_uri,
    }
    credentials = service_account.Credentials.from_service_account_info(
        GOOGLE_CREDENTIALS
    )
    client = google_speech.SpeechClient(
        credentials=credentials
    )
    content = types.RecognitionAudio(content=audio)
    # We have to match language codes here
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=lang_code,
        sample_rate_hertz=44100,
    )
    response = client.recognize(config, content)
    output = {'results': []}
    for result in response.results:
        item = {'alternatives': []}
        for alternative in result.alternatives:
            item['alternatives'].append({
                'transcript': alternative.transcript,
                'confidence': alternative.confidence
            })
        output['results'].append(item)
    return jsonify(output)