from settings import CPF_AUTH_ADMIN
from settings import PATH, LOG_NAME
from telegram.ext import ConversationHandler
import logging


logger = logging.getLogger(LOG_NAME)

chat = {}

class RegisterAdmin:

    def index(update, context):
        logger.info("Introducing registration session")
        chat_id = update.message.chat_id

        update.message.reply_text('Para cadastrar um administrador, você precisa ser um!')
        update.message.reply_text('Preciso confirmar sua identidade.')
        update.message.reply_text('Por favor, digite seu cpf:')
        logger.info("Asking for cpf")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return CPF_AUTH_ADMIN

    





    def end(update, context):
        logger.info("Canceling admin registration")
        chat_id = update.message.chat_id

        update.message.reply_text('Cadastro de admin cancelado!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END