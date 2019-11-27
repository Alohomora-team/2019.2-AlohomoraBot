"""
Handler visit interaction
"""

import logging
import requests

from checks import CheckVisitor, CheckCondo
from db.schema import visitor_exists, get_visitor_cpf
from resident.notify_resident import NotifyResident
from settings import PATH, LOG_NAME
from settings import VISIT_BLOCK, VISIT_APARTMENT
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm

logger = logging.getLogger(LOG_NAME)

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

        if not visitor_exists(chat_id):
            logger.info("Visitor is not registered - ending")
            update.message.reply_text(
                    'Você precisa ter um cadastro para fazer uma visita.'
                    )
            return ConversationHandler.END

        logger.info("Visitor is registered - proceed")

        update.message.reply_text('Bloco do morador:')
        logger.info("Asking resident block")

        logger.debug(f"data: {context.chat_data}")

        return VISIT_BLOCK

    def block(update, context):
        """
         Handle resident block
        """
        chat_id = update.message.chat_id
        block = update.message.text

        if not ValidateForm.block(block, update):
            return VISIT_BLOCK

        context.chat_data['block'] = block
        logger.debug(f"'block': '{context.chat_data['block']}'")

        check = CheckCondo.block(block)

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
        block = context.chat_data['block']

        if not ValidateForm.apartment(apartment, update):
            return VISIT_APARTMENT

        context.chat_data['apartment'] = apartment
        logger.debug(f"'apartment': '{context.chat_data['apartment']}'")

        check = CheckCondo.apartment(block, apartment)

        if 'errors' in check.keys():
            logger.error("Apartment not found - asking again")
            update.message.reply_text('Por favor, digite um apartamento existente:')
            return VISIT_APARTMENT

        logger.debug("Existing apartment - proceed")

        cpf = get_visitor_cpf(chat_id)
        name = Visit.get_visitor_name(cpf)
        name = name['data']['visitor']['completeName']

        context.chat_data['cpf'] = cpf
        context.chat_data['name'] = name

        logger.info("Notificating all residents from the apartment")
        NotifyResident.send_notification(context, context.chat_data)

        update.message.reply_text(
            'Sua entrada foi solicitada. Aguarde resposta do morador!'
        )

        logger.debug(f"data: {context.chat_data}")

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """
        logger.info("Canceling visit")

        update.message.reply_text('Visita cancelada!')

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
