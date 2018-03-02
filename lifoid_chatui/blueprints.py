# -*- coding: utf8 -*-
"""
Flask server application for Lifoid Web Chat UI
"""
import os
import base64
import boto3
from contextlib import closing
from flask import (Blueprint, render_template, request,
                   redirect, url_for, jsonify, make_response)
from flask import current_app as app
from flask_babel import refresh
from loggingmixin import ServiceLogger
from google.cloud import speech as google_speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account
from lifoid.config import settings
from lifoid import signals
from .config import ChatUIConfiguration
logger = ServiceLogger()
CHATUI_PATH = os.path.abspath(os.path.dirname(__file__))
logger.debug('Static path: {}'.format(os.path.join(CHATUI_PATH, 'static')))
chatui = Blueprint('chatui', __name__, url_prefix='/chatui',
                   template_folder='templates',
                   static_folder='static')
speech = Blueprint('speech', __name__, url_prefix='/speech')


def get_translation(_caller):
    return os.path.join(CHATUI_PATH, 'translations')


def get_conf(configuration):
    setattr(configuration, 'chatui', ChatUIConfiguration())


def get_chatui(_caller):
    return chatui


def get_speech(_caller):
    return speech


def register():
    signals.get_blueprint.connect(get_chatui)
    signals.get_blueprint.connect(get_speech)
    signals.get_conf.connect(get_conf)
    signals.get_translation.connect(get_translation)


@chatui.route('/')
def root():
    """
    Delivers Lifoid web Chat UI.
    """
    # return render_template('index.html')
    supported_languages = ['en', 'en-us', 'ja']
    lang = request.accept_languages.best_match(supported_languages)
    if lang == 'en-us' or lang is None:
        lang = 'en'
    return redirect(url_for('chatui.index', lang_code=lang))


@chatui.route('/<lang_code>')
def root_lang(lang_code):
    """
    Website root
    """
    return chatbot_lang(settings.lifoid_id, lang_code)


@chatui.route('/chatbot/<chatbot_id>')
def chatbot(chatbot_id):
    supported_languages = ['en', 'en-us', 'ja']
    lang = request.accept_languages.best_match(supported_languages)
    if lang == 'en-us' or lang is None:
        lang = 'en'
    return redirect(url_for('chatui.chatbot_lang',
                            chatbot_id=chatbot_id, lang_code=lang))


@chatui.route('/chatbot/<chatbot_id>/lang/<lang_code>')
def chatbot_lang(chatbot_id, lang_code):
    """
    Website root
    """
    logger.debug('Blueprint index invoked')
    app.config['BABEL_DEFAULT_LOCALE'] = lang_code
    refresh()
    cognito_auth = False
    if settings.cognito_auth == 'yes':
        cognito_auth = True
    return render_template(
        'index.html',
        lang=lang_code,
        path_url=settings.chatui.path_url,
        auth=cognito_auth,
        company_name=settings.chatui.company_name,
        lifoid_id=chatbot_id,
        lifoid_name=settings.lifoid_name,
        cognito_clientid=settings.cognito.client_id,
        cognito_appwebdomain=settings.cognito.appwebdomain,
        cognito_redirecturisignin=settings.cognito.redirecturisignin,
        cognito_redirecturisignout=settings.cognito.redirecturisignout,
    )


@chatui.route('/expired/<chatbot_id>/lang/<lang_code>')
def expired(chatbot_id, lang_code):
    """
    Authenticated session has expired
    """
    return render_template(
        'expired.html',
        lang=lang_code,
        lifoid_id=chatbot_id,
        cognito_appwebdomain=settings.cognito.appwebdomain,
        cognito_redirecturisignin=settings.cognito.redirecturisignin,
        cognito_clientid=settings.cognito.client_id,
        login_url='https://{}/login?redirect_uri={}&response_type=token&client_id={}&scope=email openid'.format(
            settings.cognito.appwebdomain,
            settings.cognito.redirecturisignin,
            settings.cognito.client_id
        )
    )


@chatui.route('/terms/<chatbot_id>/lang/<lang_code>')
def terms(chatbot_id, lang_code):
    """
    Terms of Use
    """
    return render_template(
        'terms.html',
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


@speech.route("/tts", methods=["POST"])
def synthesis():
    text = request.form['text']
    voice = request.form.get('voice', settings.chatui.voice)
    # For each block, invoke Polly API, which will transform text into audio
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


@speech.route("/stt", methods=["POST"])
def reco():
    audio = request.files["file"].read()
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
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=settings.chatui.lang_reco,
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