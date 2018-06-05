"""
Flask server application for Lifoid Web Chat UI
"""
import os
import base64
import json
from contextlib import closing
import boto3
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
from lifoid.auth import get_user
from lifoid_agent.repository import get_agent_conf

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


@chatui.route('/', methods=['GET'])
def root():
    """
    Delivers Lifoid web Chat UI.
    """
    default_lifoid_id = settings.lifoid_id
    bot_conf = get_agent_conf(default_lifoid_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    lang = get_lang(bot_conf)
    return redirect(url_for('chatui.chatbot_lang',
                            lifoid_id=default_lifoid_id, lang_code=lang))


@chatui.route('/<lang_code>', methods=['GET'])
def root_lang(lang_code):
    """
    Website root
    """
    return chatbot_lang(settings.lifoid_id, lang_code)


@chatui.route('/chatbot/<lifoid_id>', methods=['GET'])
def chatbot(lifoid_id):
    bot_conf = get_agent_conf(lifoid_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    lang = get_lang(bot_conf)
    return redirect(url_for('chatui.chatbot_lang',
                            lifoid_id=lifoid_id, lang_code=lang))


@chatui.route('/chatbot/<lifoid_id>/lang/<lang_code>', methods=['GET'])
def chatbot_lang(lifoid_id, lang_code):
    """
    website root
    """
    logger.debug('blueprint index invoked')
    logger.debug('settings dev_auth: {}'.format(settings.dev_auth))
    app.config['babel_default_locale'] = lang_code.replace('-', '_')
    refresh()
    bot_conf = get_agent_conf(lifoid_id)
    if bot_conf is None:
        return make_response('unknown bot', 404)
    try:
        return render_template(
            'index.html',
            chat_menu=bot_conf['chatui']['chat_menu'],
            languages=bot_conf['languages'],
            color=bot_conf['chatui']['color'],
            color_active=bot_conf['chatui']['color_active'],
            lang=lang_code,
            path_url=settings.chatui.path_url,
            auth=settings.chatui.login == 'yes',
            company_name=bot_conf['chatui']['company_name'],
            lifoid_id=lifoid_id,
            lifoid_name=bot_conf['chatui']['service_name'],
            cognito_clientid=bot_conf['auth']['client_id'],
            cognito_appwebdomain=bot_conf['auth']['web_domain'],
            cognito_redirecturisignin=bot_conf['auth']['url_signin'],
            cognito_redirecturisignout=bot_conf['auth']['url_signout'],
            user_id='test',
            username='test',
            access_token='token'
        )
    except UnknownLocaleError:
        return make_response('not supported locale', 404)


@chatui.route('/expired/<lifoid_id>/lang/<lang_code>', methods=['GET'])
def expired(lifoid_id, lang_code):
    """
    Authenticated session has expired
    """
    bot_conf = get_agent_conf(lifoid_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    app.config['BABEL_DEFAULT_LOCALE'] = lang_code.replace('-', '_')
    refresh()
    return render_template(
        'expired.html',
        lifoid_name=bot_conf['chatui']['service_name'],
        lang=lang_code,
        lifoid_id=lifoid_id,
        cognito_clientid=bot_conf['auth']['client_id'],
        cognito_appwebdomain=bot_conf['auth']['web_domain'],
        cognito_redirecturisignin=bot_conf['auth']['url_signin'],
        cognito_redirecturisignout=bot_conf['auth']['url_signout']
    )


@chatui.route('/terms/<lifoid_id>/lang/<lang_code>', methods=['GET'])
def terms(lifoid_id, lang_code):
    """
    Terms of Use
    """
    bot_conf = get_agent_conf(lifoid_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    app.config['BABEL_DEFAULT_LOCALE'] = lang_code.replace('-', '_')
    refresh()
    return render_template(
        'terms.html',
        lifoid_name=bot_conf['chatui']['service_name'],
        lang=lang_code,
        lifoid_id=lifoid_id,
    )


@chatui.route('/privacy/<lifoid_id>/lang/<lang_code>', methods=['GET'])
def privacy(lifoid_id, lang_code):
    """
    Privacy Policy
    """
    bot_conf = get_agent_conf(lifoid_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    app.config['BABEL_DEFAULT_LOCALE'] = lang_code.replace('-', '_')
    refresh()
    return render_template(
        'privacy.html',
        lang=lang_code,
        lifoid_id=lifoid_id,
    )


@speech.route("/chatbot/<lifoid_id>/lang/<lang_code>/tts", methods=["POST"])
def synthesis(lifoid_id, lang_code):
    data = json.loads(request.get_data())
    user = get_user(data)
    if user is None:
        abort(403)
    text = data['q']['text']
    voice = request.form.get('voice', settings.chatui.voice)
    bot_conf = get_agent_conf(lifoid_id)
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


@speech.route("/chatbot/<lifoid_id>/lang/<lang_code>/stt", methods=["POST"])
def reco(lifoid_id, lang_code):
    if 'data' not in request.form:
        abort(404)
    data = json.loads(request.form['data'])
    user = get_user(data)
    if user is None:
        abort(403)
    audio = request.files["file"].read()
    bot_conf = get_agent_conf(lifoid_id)
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


@chatui.route('/chatbot/<lifoid_id>/token/<token>', methods=['GET'])
def chatbot_token(lifoid_id, token):
    bot_conf = get_agent_conf(lifoid_id)
    if bot_conf is None:
        return make_response('Unknown Bot', 404)
    lang = get_lang(bot_conf)
    return redirect(url_for('chatui.chatbot_token_lang',
                            lifoid_id=lifoid_id, token=token,
                            lang_code=lang))


@chatui.route('/chatbot/<lifoid_id>/token/<token>/lang/<lang_code>', methods=['GET'])
def chatbot_token_lang(lifoid_id, token, lang_code):
    logger.debug('blueprint otqr_lang invoked')
    logger.debug('settings dev_auth: {}'.format(settings.dev_auth))
    app.config['babel_default_locale'] = lang_code.replace('-', '_')
    refresh()
    bot_conf = get_agent_conf(lifoid_id)
    if bot_conf is None:
        return make_response('unknown bot', 404)
    try:
        return render_template(
            'index.html',
            chat_menu=bot_conf['chatui']['chat_menu'],
            languages=bot_conf['languages'],
            color=bot_conf['chatui']['color'],
            color_active=bot_conf['chatui']['color_active'],
            lang=lang_code,
            path_url=settings.chatui.path_url,
            auth=settings.chatui.login == 'yes',
            company_name=bot_conf['chatui']['company_name'],
            lifoid_id=lifoid_id,
            lifoid_name=bot_conf['chatui']['service_name'],
            cognito_clientid=bot_conf['auth'].get('client_id', ''),
            cognito_appwebdomain=bot_conf['auth'].get('web_domain', ''),
            cognito_redirecturisignin=bot_conf['auth'].get('url_signin', ''),
            cognito_redirecturisignout=bot_conf['auth'].get('url_signout', ''),
            user_id=token,
            username=token,
            access_token=token
        )
    except UnknownLocaleError:
        return make_response('not supported locale', 404)
