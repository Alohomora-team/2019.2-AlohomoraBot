"""
Handler visitor interaction
"""
import logging
import requests

from settings import *
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from validator import ValidateForm
from checks import CheckVisitor, CheckCondo
from db.schema import visitor_exists, get_visitor_cpf
from resident.notify_resident import NotifyResident

logger = logging.getLogger(LOG_NAME)

chat = {}

class Visit:
    """
    Functions that handlers visitors interactions
    """

    def index(update, context):
        """
        Start interactions
        """
        logger.info("introducing visitor session")
        chat_id = update.message.chat_id


        update.message.reply_text(
                'Iniciando procedimento de visita. Digite /cancelar para interromper'
                )

        if not visitor_exists(chat_id):
            logger.info("Visitor is not registered - canceling")
            update.message.reply_text(
                    'Você não está cadastrado. Digite /cadastrar_visitante para se registrar'
                    )
            return ConversationHandler.END

        logger.info("Visitor is registered - proceed")

        update.message.reply_text('Informe o bloco do morador:')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return VISIT_BLOCK

    def block(update, context):
        """
        Validate block
        """
        chat_id = update.message.chat_id
        block = update.message.text

        if not ValidateForm.block(block, update):
            return VISIT_BLOCK

        chat[chat_id]['block'] = block
        logger.debug(f"'block': '{chat[chat_id]['block']}'")

        check = CheckCondo.block(chat, chat_id)

        if 'errors' in check.keys():
            logger.error("Block not found - asking again")
            update.message.reply_text('Por favor, digite um bloco existente:')
            return VISIT_BLOCK

        logger.debug("Existing block - proceed")

        update.message.reply_text('Apartamento:')
        logger.info("Asking for apartment number")

        return VISIT_APARTMENT

    def apartment(update, context):
        """
        Validate apartment
        """

        chat_id = update.message.chat_id
        apartment = update.message.text

        if not ValidateForm.apartment(apartment, update):
            return VISIT_APARTMENT

        chat[chat_id]['apartment'] = apartment
        logger.debug(f"'apartment': '{chat[chat_id]['apartment']}'")

        check = CheckCondo.apartment(chat, chat_id)

        if 'errors' in check.keys():
            logger.error("Apartment not found - asking again")
            update.message.reply_text('Por favor, digite um apartamento existente:')
            return VISIT_APARTMENT

        logger.debug("Existing apartment - proceed")

        cpf = get_visitor_cpf(chat_id)
        name = Visit.get_visitor_name(cpf)
        name = name['data']['visitor']['completeName']

        chat[chat_id]['cpf'] = cpf
        chat[chat_id]['name'] = name

        logger.info("Notificating all residents from the apartment")
        NotifyResident.send_notification(context, chat[chat_id])

        update.message.reply_text(
            'Sua entrada foi solicitada. Aguarde resposta do morador!'
        )

        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        chat[chat_id] = {}

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """
        logger.info("Canceling visit")
        chat_id = update.message.chat_id

        update.message.reply_text('Visita cancelada!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

    def get_visitor_name(cpf):
        """
        Get in database the visitor name
        """
        logger.info("Getting the visitor name")
        query = """
        query visitor($cpf: String!){
            visitor(cpf: $cpf) {
                completeName
            }
        }
        """

        variables = {
            'cpf': cpf
            }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response.json()
