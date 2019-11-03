import logging
import requests
from settings import *
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from validator import ValidateForm
from checks import CheckVisitor, CheckCondo

LOGGER = logging.getLogger(LOG_NAME)

CHAT = {}

class Visit:

    def index(update, context):
        LOGGER.info("Introducing visitor session")
        chat_id = update.message.chat_id

        update.message.reply_text('Caso deseje interromper o processo digite /cancelar')
        LOGGER.info("Checking if visitor has registration")

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        yes_keyboard = KeyboardButton('Sim')
        no_keyboard = KeyboardButton('Não')
        keyboard = [[yes_keyboard], [no_keyboard]]
        response = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Você já possui cadastro?', reply_markup=response)

        return VERIFY_REGISTRATION

    def verify_registration(update, context):
        chat_id = update.message.chat_id
        response = update.message.text

        if not ValidateForm.boolean_value(response, update):
            return VERIFY_REGISTRATION

        if response == "Sim":
            LOGGER.info("Visitor replied that he has registration")
            update.message.reply_text('Ok! Nos diga seu CPF:')
            return VISITOR_CPF

        else:
            update.message.reply_text('Ok! Então vamos fazer o seu cadastro!')
            LOGGER.info("Visitor replied that he hasn't registration")
            update.message.reply_text('Qual o seu nome completo?')
            return VISITOR_REGISTER_NAME

    def cpf(update, context):
        chat_id = update.message.chat_id
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return VISITOR_CPF

        cpf = ValidateForm.cpf(cpf, update)

        CHAT[chat_id]['cpf'] = cpf
        LOGGER.debug(f"'cpf': '{CHAT[chat_id]['cpf']}'")

        check = CheckVisitor.cpf(CHAT, chat_id)

        #if visitor have registration into database
        if 'errors' not in check.keys():
            LOGGER.error("Visit have register")
            completeName = check['data']['visitor']['completeName']
            update.message.reply_text(
                "Ok %s, agora nos diga a qual bloco deseja ir:" % completeName
            )
            return VISITOR_BLOCK

        else:
            update.message.reply_text("CPF não encontrado. Por favor, tente novamente")
            return VISITOR_CPF


    def block(update, context):
        chat_id = update.message.chat_id
        block = update.message.text

        if not ValidateForm.block(block, update):
            return VISITOR_BLOCK

        CHAT[chat_id]['block'] = block
        LOGGER.debug(f"'block': '{CHAT[chat_id]['block']}'")

        check = CheckCondo.block(CHAT, chat_id)

        if 'errors' in check.keys():
            LOGGER.error("Block not found - asking again")
            update.message.reply_text('Por favor, digite um bloco existente:')
            return VISITOR_BLOCK

        LOGGER.debug("Existing block - proceed")

        update.message.reply_text('Apartamento:')
        LOGGER.info("Asking for apartment number")

        return VISITOR_APARTMENT

    def apartment(update, context):

        chat_id = update.message.chat_id
        apartment = update.message.text

        if not ValidateForm.apartment(apartment, update):
            return VISITOR_APARTMENT

        CHAT[chat_id]['apartment'] = apartment
        LOGGER.debug(f"'apartment': '{CHAT[chat_id]['apartment']}'")

        check = CheckCondo.apartment(CHAT, chat_id)

        if 'errors' in check.keys():
            LOGGER.error("Apartment not found - asking again")
            update.message.reply_text('Por favor, digite um apartamento existente:')
            return VISITOR_APARTMENT

        LOGGER.debug("Existing apartment - proceed")

        response = Visit.create_entry(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            LOGGER.info("Entry visitor registered in database")
            update.message.reply_text(
                'Sua solicitação de entrada foi criada. Aguarde resposta do morador!'
            )
        else:
            LOGGER.error("Entry visitor registration failed")
            update.message.reply_text('Falha no sistema!')

        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        CHAT[chat_id] = {}

        return ConversationHandler.END

    def create_entry(chat_id):
        LOGGER.debug("Creating new visitor entry")

        query = """
        mutation createEntryVisitor(
            $visitorCpf: String!,
            $blockNumber: String!,
            $apartmentNumber: String!,
            $pending: Boolean!
            ){
            createEntryVisitor(
                visitorCpf: $visitorCpf,
                blockNumber: $blockNumber,
                apartmentNumber: $apartmentNumber,
                pending: $pending,
            ){
                pending
            }
        }
        """

        variables = {
                'visitorCpf': CHAT[chat_id]['cpf'],
                'blockNumber': CHAT[chat_id]['block'],
                'apartmentNumber': CHAT[chat_id]['apartment'],
                'pending': True,
                }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        LOGGER.debug(f"Response: {response.json()}")

        return response

    def end(update, context):
        LOGGER.info("Canceling visit")
        chat_id = update.message.chat_id

        update.message.reply_text('Visita cancelada!')

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return ConversationHandler.END