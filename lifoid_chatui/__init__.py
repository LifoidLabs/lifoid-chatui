# -*- coding: utf8 -*-
"""
Flask server application for Lifoid Web Chat UI
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app
from flask_babel import refresh
from loggingmixin import ServiceLogger
from lifoid.config import settings
from lifoid import signals
logger = ServiceLogger()
CHATUI_PATH = os.path.abspath(os.path.dirname(__file__))
logger.debug('Static path: {}'.format(os.path.join(CHATUI_PATH, 'static')))
chatui = Blueprint('chatui', __name__, url_prefix='/chatui',
                   template_folder='templates',
                   static_folder='static')


__version__ = '0.1.0'


def get_translation(_caller):
    return os.path.join(CHATUI_PATH, 'translations')


def get_blueprint(_caller):
    return chatui


def register():
    signals.get_blueprint.connect(get_blueprint)
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
def index(lang_code):
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
        path_url=settings.path_url,
        auth=cognito_auth,
        company_name=settings.company_name,
        lifoid_id=settings.lifoid_id,
        lifoid_name=settings.lifoid_name,
        cognito_clientid=settings.cognito.client_id,
        cognito_appwebdomain=settings.cognito.appwebdomain,
        cognito_redirecturisignin=settings.cognito.redirecturisignin,
        cognito_redirecturisignout=settings.cognito.redirecturisignout,
    )


@chatui.route('/<lang_code>/expired')
def expired(lang_code):
    """
    Authenticated session has expired
    """
    return render_template(
        'expired.html',
        lang=lang_code,
        login_url='https://{}/login?redirect_uri={}&response_type=token&client_id={}&scope=email openid'.format(
            settings.cognito.appwebdomain,
            settings.cognito.redirecturisignin,
            settings.cognito.client_id
        )
    )


@chatui.route('/<lang_code>/terms')
def terms(lang_code):
    """
    Terms of Use
    """
    return render_template(
        'terms.html',
        lang=lang_code,
        lifoid_id=settings.lifoid_id,
    )


@chatui.route('/<lang_code>/privacy')
def privacy(lang_code):
    """
    Privacy Policy
    """
    return render_template(
        'privacy.html',
        lang=lang_code,
        lifoid_id=settings.lifoid_id,
    )
