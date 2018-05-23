# -*- coding: utf8 -*-
"""
Dialogflow plugin ocnfiguration
Author: Romary Dupuis <romary@me.com>
"""
from lifoid.config import Configuration, environ_setting


class ChatUIConfiguration(Configuration):
    """
    Configuration for the database server
    """
    login = environ_setting('LOGIN', 'no', required=False)
    path_url = environ_setting('PATH_URL', '', required=False)
    company_name = environ_setting('COMPANY_NAME', 'Company', required=False)
    voice = environ_setting('SPEECH_VOICE', 'Matthew', required=False)
    lang_reco = environ_setting('LANG_RECO', 'en-us', required=False)
    google_speech_id = environ_setting('GOOGLE_SPEECH_ID', None, required=False)
    google_speech_key = environ_setting('GOOGLE_SPEECH_KEY', None, required=False)
    google_speech_email = environ_setting('GOOGLE_SPEECH_EMAIL', None, required=False)
    google_speech_token_uri = environ_setting('GOOGLE_SPEECH_TOKEN_URI', None, required=False)
