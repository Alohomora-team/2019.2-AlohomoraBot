from settings import LOG_NAME
from settings import VISITOR_REGISTER_NAME, VISITOR_REGISTER_CPF
from settings import PATH
from checks import CheckVisitor
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

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        chat[chat_id]['name'] = name
        logger.debug(f"'name': '{chat[chat_id]['name']}'")

        update.message.reply_text('Ok! Agora nos diga seu CPF:')

        return VISITOR_REGISTER_CPF

    def cpf(update, context):
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

        logger.info("Asking for block number")

        update.message.reply_text('Deu bom, agora enviar a mutation!!!!')

        response = RegisterVisitor.register_visitor(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Visitor registered in database")
            update.message.reply_text('Visitante cadastrado no sistema!')
            update.message.reply_text('Para efetuar uma visita, digite /visitar')
        else:
            logger.error("Visitor registration failed")
            update.message.reply_text('Falha ao cadastrar visitante no sistema!')

        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        chat[chat_id] = {}

        return ConversationHandler.END

    def register_visitor(chat_id):
        logger.info("Registering visitor")
        query = """
        mutation createVisitor(
            $completeName: String!,
            $cpf: String!
            ){
            createVisitor(
                completeName: $completeName,
                cpf: $cpf
            ){
                completeName
                cpf
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
