from settings import LOG_NAME
from settings import SHOW_ENTRIES_PENDING, CPF_AUTH
from settings import PATH
from checks import CheckVisitor
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from validator import ValidateForm
import logging
import requests

logger = logging.getLogger(LOG_NAME)

chat = {}

class HandleEntryVisitors:

    def index(update, context):
        logger.info("Introducing handle entry visitor session")
        chat_id = update.message.chat_id

        update.message.reply_text('Ok. Antes de começar, precisamos de alguns dados:')
        update.message.reply_text('Caso deseje interromper o processo digite /cancelar')
        update.message.reply_text('CPF:')
        logger.info("Asking for CPF")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return CPF_AUTH

    def show_entries_pending(update, context):
        logger.info("Show visitor entries pending")
        chat_id = update.message.chat_id