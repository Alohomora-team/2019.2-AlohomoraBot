from settings import VISITOR_CPF, VISITOR_BLOCK, VERIFY_REGISTRATION, LOG_NAME
from telegram.ext import ConversationHandler
from validator import ValidateForm
from checks import CheckVisitor
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

        if response == "sim":
            logger.info("Visitor replied that he has registration")
            update.message.reply_text('Ok! Nos diga seu CPF:')
            return VISITOR_CPF

        # else:
        #     return VISITOR_REGISTRATION

        update.message.reply_text('Entrei!')
        
    def cpf(update, context):
        chat_id = update.message.chat_id
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return VISITOR_CPF

        cpf = ValidateForm.cpf(cpf, update)

        chat[chat_id]['cpf'] = cpf
        logger.debug(f"'cpf': '{chat[chat_id]['cpf']}'")

        check = CheckVisitor.cpf(chat, chat_id)
        #Deu bom
        if 'errors' not in check.keys():
            logger.error("Visit have register")
            completeName = check['data']['visitor']['completeName']
            update.message.reply_text("Ok %s, agora nos diga a qual bloco deseja ir:" % completeName)
            return VISITOR_BLOCK

    def block(update, context):

        update.message.reply_text('Entrei!')


    def end(update, context):
        logger.info("Canceling visit")
        chat_id = update.message.chat_id

        update.message.reply_text('Visita cancelada!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END