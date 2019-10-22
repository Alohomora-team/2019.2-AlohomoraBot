from settings import VERIFY_REGISTRATION, LOG_NAME
from telegram.ext import ConversationHandler
from validator import ValidateForm
import logging
import requests

logger = logging.getLogger(LOG_NAME)

chat = {}

class Visit:

    def index(update, context):
        logger.info("Introducing visitor session")
        chat_id = update.message.chat_id

        update.message.reply_text('Você já possui cadastro? Digite apenas sim ou nao')
        update.message.reply_text('Caso deseje interromper o processo digite /cancelar')
        logger.info("Checking if visitor has registration")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return VERIFY_REGISTRATION

    def verify_registration(update, context):
        chat_id = update.message.chat_id
        response = update.message.text
        
        if not ValidateForm.boolean_value(response, update):
            return VERIFY_REGISTRATION

        update.message.reply_text('Entrei!')
        

    def end(update, context):
        logger.info("Canceling visit")
        chat_id = update.message.chat_id

        update.message.reply_text('Visita cancelada!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END