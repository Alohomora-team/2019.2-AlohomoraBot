"""
Interactions to register a visitor
"""

import logging
import requests

from checks import CheckVisitor
from db.schema import create_visitor, visitor_exists
from settings import LOG_NAME, PATH
from settings import VISITOR_REGISTER_NAME, VISITOR_REGISTER_CPF
from telegram.ext import ConversationHandler
from validator import ValidateForm

logger = logging.getLogger(LOG_NAME)

class RegisterVisitor:
    """
    Register visitor
    """
    def index(update, context):
        """
        Start the interaction
        """
        logger.info("Introducing visitor registration session")
        chat_id = update.message.chat_id

        if visitor_exists(chat_id):
            logger.info("Visitor already registered - ending")
            update.message.reply_text("Você já possui um cadastro!")
            return ConversationHandler.END

        update.message.reply_text("Nome:")
        logger.info("Asking for name")

        logger.debug(f"data: {context.chat_data}")

        return VISITOR_REGISTER_NAME

    def name(update, context):
        """
        Get name interaction
        """
        name = update.message.text

        if not ValidateForm.name(name, update):
            return VISITOR_REGISTER_NAME

        context.chat_data['name'] = name
        logger.debug(f"'name': '{context.chat_data['name']}'")

        update.message.reply_text('CPF:')
        logger.info("Asking for CPF")

        return VISITOR_REGISTER_CPF

    def cpf(update, context):
        """
        Get cpf interaction
        """
        chat_id = update.message.chat_id
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return VISITOR_REGISTER_CPF

        cpf = ValidateForm.cpf(cpf, update)

        context.chat_data['cpf'] = cpf
        logger.debug(f"'cpf': '{context.chat_data['cpf']}'")

        check = CheckVisitor.cpf(cpf)

        if 'errors' not in check.keys():
            logger.error("CPF already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este CPF, tente novamente:')
            return VISITOR_REGISTER_CPF

        logger.debug("Available CPF - proceed")

        response = RegisterVisitor.register_visitor(context.chat_data)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Visitor registered in database")
            update.message.reply_text('Você foi cadastrado no sistema!')
            create_visitor(
                    cpf=cpf,
                    chat_id=chat_id
                    )

        else:
            logger.error("Visitor registration failed")
            update.message.reply_text('Falha ao cadastrar no sistema!')

        logger.debug(f"data: {context.chat_data}")

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """
        logger.info("Canceling visitor registration")

        update.message.reply_text('Cadastro cancelado!')

        return ConversationHandler.END

    def register_visitor(data):
        """
        Register a registor interaction
        """

        logger.info("Registering visitor")
        query = """
        mutation createVisitor(
            $completeName: String!,
            $cpf: String!
            ){
            createVisitor(
                completeName: $completeName,
                cpf: $cpf
            ) {
                visitor {
                    id
                    completeName
                    cpf
                }
            }
        }
        """

        variables = {
            'completeName':data['name'],
            'cpf': data['cpf']
            }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response
