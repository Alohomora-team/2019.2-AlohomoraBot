from settings import VISITOR_CPF, VISITOR_BLOCK, VISITOR_APARTMENT, VERIFY_REGISTRATION, LOG_NAME
from telegram.ext import ConversationHandler
from validator import ValidateForm
from checks import CheckVisitor, CheckCondo
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
        
        #if visitor have registration into database
        if 'errors' not in check.keys():
            logger.error("Visit have register")
            completeName = check['data']['visitor']['completeName']
            update.message.reply_text("Ok %s, agora nos diga a qual bloco deseja ir:" % completeName)
            return VISITOR_BLOCK

        # else:
        #     return VISITOR_REGISTRATION


    def block(update, context):
        chat_id = update.message.chat_id
        block = update.message.text

        if not ValidateForm.block(block, update):
            return VISITOR_BLOCK

        chat[chat_id]['block'] = block
        logger.debug(f"'block': '{chat[chat_id]['block']}'")

        check = CheckCondo.block(chat, chat_id)

        if 'errors' in check.keys():
            logger.error("Block not found - asking again")
            update.message.reply_text('Por favor, digite um bloco existente:')
            return VISITOR_BLOCK

        logger.debug("Existing block - proceed")

        update.message.reply_text('Apartamento:')
        logger.info("Asking for apartment number")

        return VISITOR_APARTMENT

    def apartment(update, context):

        update.message.reply_text('Entrei!')
        # chat_id = update.message.chat_id
        # apartment = update.message.text

        # if not ValidateForm.apartment(apartment, update):
        #     return APARTMENT

        # chat[chat_id]['apartment'] = apartment
        # logger.debug(f"'apartment': '{chat[chat_id]['apartment']}'")

        # check = CheckCondo.apartment(chat, chat_id)

        # if 'errors' in check.keys():
        #     logger.error("Apartment not found - asking again")
        #     update.message.reply_text('Por favor, digite um apartamento existente:')
        #     return APARTMENT

        # logger.debug("Existing apartment - proceed")

        # update.message.reply_text(
        #     'Vamos agora cadastrar a sua voz! Grave uma breve mensagem de voz dizendo "Juro que sou eu"')

        # logger.info("Requesting voice audio")

        # return VOICE_REGISTER


    def end(update, context):
        logger.info("Canceling visit")
        chat_id = update.message.chat_id

        update.message.reply_text('Visita cancelada!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END