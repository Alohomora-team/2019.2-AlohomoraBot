"""
Visitor reponses
"""
import logging
import requests

from settings import *
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from validator import ValidateForm
from checks import CheckVisitor, CheckCondo

logger = logging.getLogger(LOG_NAME)

chat = {}

class Visit:
    """
    User interactions
    """

    # TODO(bumbleblo) that functions don't have a good name
    def index(update, context):
        """
        Verify if user has a register
        """
        logger.info("Introducing visitor session")
        chat_id = update.message.chat_id

        update.message.reply_text('Caso deseje interromper o processo digite /cancelar')
        logger.info("Checking if visitor has registration")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        yes_keyboard = KeyboardButton('Sim')
        no_keyboard = KeyboardButton('Não')
        keyboard = [[yes_keyboard], [no_keyboard]]
        response = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Você já possui cadastro?', reply_markup=response)

        return VERIFY_REGISTRATION

    def verify_registration(update, context):
        """
        Verify if visitor is registered
        """
        chat_id = update.message.chat_id
        response = update.message.text

        if not ValidateForm.boolean_value(response, update):
            return VERIFY_REGISTRATION

        if response == "Sim":
            logger.info("Visitor replied that he has registration")
            update.message.reply_text('Ok! Nos diga seu CPF:')
            return VISITOR_CPF

        else:
            update.message.reply_text('Ok! Então vamos fazer o seu cadastro!')
            logger.info("Visitor replied that he hasn't registration")
            update.message.reply_text('Qual o seu nome completo?')
            return VISITOR_REGISTER_NAME

    def cpf(update, context):
        """
        Verify visitor cpf
        """
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
            firstName = completeName.split(' ')[0]
            update.message.reply_text("Ok %s, agora nos diga a qual bloco deseja ir:" % firstName)
            return VISITOR_BLOCK

        else:
            update.message.reply_text("CPF não encontrado. Por favor, tente novamente")
            return VISITOR_CPF


    def block(update, context):
        """
        Get block of interest
        """
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
        """
        Get apartment intention
        """

        chat_id = update.message.chat_id
        apartment = update.message.text

        if not ValidateForm.apartment(apartment, update):
            return VISITOR_APARTMENT

        chat[chat_id]['apartment'] = apartment
        logger.debug(f"'apartment': '{chat[chat_id]['apartment']}'")

        check = CheckCondo.apartment(chat, chat_id)

        if 'errors' in check.keys():
            logger.error("Apartment not found - asking again")
            update.message.reply_text('Por favor, digite um apartamento existente:')
            return VISITOR_APARTMENT

        logger.debug("Existing apartment - proceed")

        response = Visit.create_entry(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Entry visitor registered in database")
            update.message.reply_text(
                'Sua solicitação de entrada foi criada. Aguarde resposta do morador!'
            )
        else:
            logger.error("Entry visitor registration failed")
            update.message.reply_text('Falha no sistema!')

        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        chat[chat_id] = {}

        return ConversationHandler.END

    def create_entry(chat_id):
        """
        Create a visitor entry request
        """
        logger.debug("Creating new visitor entry")

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
                entryVisitor {
                    id
                    date
                    pending
                    }
            }
        }
        """

        variables = {
                'visitorCpf': chat[chat_id]['cpf'],
                'blockNumber': chat[chat_id]['block'],
                'apartmentNumber': chat[chat_id]['apartment'],
                'pending': True,
                }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response

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
