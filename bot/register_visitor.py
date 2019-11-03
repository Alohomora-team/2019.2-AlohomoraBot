import logging
import requests
from settings import LOG_NAME, PATH
from settings import VISITOR_REGISTER_NAME, VISITOR_REGISTER_CPF, VISITOR_BLOCK
from checks import CheckVisitor
from telegram.ext import ConversationHandler
from validator import ValidateForm

LOGGER = logging.getLogger(LOG_NAME)

CHAT = {}

class RegisterVisitor:

    def name(update, context):
        chat_id = update.message.chat_id
        name = update.message.text

        if not ValidateForm.name(name, update):
            return VISITOR_REGISTER_NAME

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        CHAT[chat_id]['name'] = name
        LOGGER.debug(f"'name': '{CHAT[chat_id]['name']}'")

        update.message.reply_text('Ok! Agora nos diga seu CPF:')

        return VISITOR_REGISTER_CPF

    def cpf(update, context):
        chat_id = update.message.chat_id
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return VISITOR_REGISTER_CPF

        cpf = ValidateForm.cpf(cpf, update)

        CHAT[chat_id]['cpf'] = cpf
        LOGGER.debug(f"'cpf': '{CHAT[chat_id]['cpf']}'")

        check = CheckVisitor.cpf(CHAT, chat_id)

        if 'errors' not in check.keys():
            LOGGER.error("CPF already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este CPF, tente novamente:')
            return VISITOR_REGISTER_CPF

        LOGGER.debug("Available CPF - proceed")

        response = RegisterVisitor.register_visitor(chat_id)


        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            LOGGER.info("Visitor registered in database")
            update.message.reply_text('Você foi cadastrado no sistema!')
            update.message.reply_text('Para visitar algum morador, digite /visitar')

        else:
            LOGGER.error("Visitor registration failed")
            update.message.reply_text('Falha ao cadastrar visitante no sistema!')

        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")
        CHAT[chat_id] = {}

        return ConversationHandler.END

    def register_visitor(chat_id):
        LOGGER.info("Registering visitor")
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
            'completeName': CHAT[chat_id]['name'],
            'cpf': CHAT[chat_id]['cpf']
            }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        LOGGER.debug(f"Response: {response.json()}")

        return response
