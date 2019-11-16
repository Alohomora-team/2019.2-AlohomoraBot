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

chat = {}

class RegisterVisitor:
    """
    Register visitor
    """
    def index(update, context):
        """
        Start the conversation
        """
        logger.info("Introducing visitor registration session")
        chat_id = update.message.chat_id

        if visitor_exists(chat_id):
            update.message.reply_text("Já existe um visitante registrado neste celular!")
            logger.info("Visitor chat_id already in database. Ending conversation")
            return ConversationHandler.END

        update.message.reply_text("Por favor, informe seu nome:")
        logger.info("Asking for name")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return VISITOR_REGISTER_NAME

    def name(update, context):
        """
        Get name interaction
        """
        chat_id = update.message.chat_id
        name = update.message.text

        if not ValidateForm.name(name, update):
            return VISITOR_REGISTER_NAME

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        chat[chat_id]['name'] = name
        logger.debug(f"'name': '{chat[chat_id]['name']}'")

        update.message.reply_text('Agora digite seu CPF:')
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

        chat[chat_id]['cpf'] = cpf
        logger.debug(f"'cpf': '{chat[chat_id]['cpf']}'")

        check = CheckVisitor.cpf(chat, chat_id)

        if 'errors' not in check.keys():
            logger.error("CPF already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este CPF, tente novamente:')
            return VISITOR_REGISTER_CPF

        logger.debug("Available CPF - proceed")

        response = RegisterVisitor.register_visitor(chat_id)


        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Visitor registered in database")
            update.message.reply_text('Você foi cadastrado no sistema!')
            update.message.reply_text('Para visitar algum morador, digite /visitar')
            create_visitor(
                    cpf=cpf,
                    chat_id=chat_id
                    )

        else:
            logger.error("Visitor registration failed")
            update.message.reply_text('Falha ao cadastrar visitante no sistema!')

        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")
        chat[chat_id] = {}

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """
        logger.info("Canceling visitor registration")
        chat_id = update.message.chat_id

        update.message.reply_text('Cadastro cancelado!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

    def register_visitor(chat_id):
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
            'completeName': chat[chat_id]['name'],
            'cpf': chat[chat_id]['cpf']
            }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response
