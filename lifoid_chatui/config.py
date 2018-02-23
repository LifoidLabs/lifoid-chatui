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
    path_url = environ_setting('PATH_URL', '', required=False)
    company_name = environ_setting('COMPANY_NAME', 'Company', required=False)
    voice = environ_setting('SPEECH_VOICE', 'Matthew', required=False)
    lang_reco = environ_setting('LANG_RECO', 'en-us', required=False)