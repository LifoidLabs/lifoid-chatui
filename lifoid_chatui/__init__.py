# -*- coding: utf8 -*-
"""
Flask server application for Lifoid Web Chat UI
"""
__version__ = '0.1.0'
import os
from lifoid import signals
from .blueprints import chatui, speech, CHATUI_PATH
from .config import ChatUIConfiguration


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
