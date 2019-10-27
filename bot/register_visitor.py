from settings import LOG_NAME
from settings import VISITOR_REGISTER_NAME
from settings import PATH

from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup

from validator import ValidateForm

import logging
import requests

logger = logging.getLogger(LOG_NAME)

chat = {}

class RegisterVisitor:

    def name(update, context):
        chat_id = update.message.chat_id
        name = update.message.text

        if not ValidateForm.name(name, update):
            return VISITOR_REGISTER_NAME

        chat[chat_id]['name'] = name
        logger.debug(f"'name': '{chat[chat_id]['name']}'")

        update.message.reply_text('Ok! Agora nos diga seu CPF:')