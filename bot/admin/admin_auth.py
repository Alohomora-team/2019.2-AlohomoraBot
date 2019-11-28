"""
Authenticate a admin
"""

import logging
import requests

from checks import CheckAdmin
from db.schema import admin_exists, create_admin
from settings import ADMIN_AUTH_EMAIL, ADMIN_AUTH_PWD, ADMIN_AUTH_REPEAT
from settings import LOG_NAME, PATH
from telegram.ext import ConversationHandler
from validator import ValidateForm

logger = logging.getLogger(LOG_NAME)

class AdminAuth:
    """
    Authenticate a admin
    """
    def index(update, context):
        """
        Start the conversation
        """
        logger.info("Introducing authentication session")
        update = update.callback_query
        chat_id = update.message.chat_id

        if admin_exists(chat_id):
            logger.info("Admin already authenticated - ending")
            update.message.reply_text('Você já está autenticado!')

            context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=update.message.message_id,
                    )
            return ConversationHandler.END
        else:
            context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=update.message.message_id,
                    text="""
Digite /cancelar caso queira interromper o processo.
                    """
                    )

        update.message.reply_text('Email:')
        logger.info("Asking for email")

        logger.debug(f"data: {context.chat_data}")

        return ADMIN_AUTH_EMAIL

    def email(update, context):
        """
        Get email to authenticate admin
        """
        email = update.message.text

        if not ValidateForm.email(email, update):
            return ADMIN_AUTH_EMAIL

        context.chat_data['email'] = email
        logger.debug(f"'email': '{context.chat_data['email']}'")

        check = CheckAdmin.email(email)

        if 'errors' not in check.keys():
            logger.debug("Email exists in database - proceed")
            update.message.reply_text('Senha:')
            logger.info("Requesting password")
            return ADMIN_AUTH_PWD

        else:
            update.message.reply_text("Email não encontrado. Por favor, digite novamente:")
            return ADMIN_AUTH_EMAIL

    def password(update, context):
        """
        Get password to authenticate admin
        """
        chat_id = update.message.chat_id
        password = update.message.text

        context.chat_data['password'] = password
        logger.debug(f"'password': '{context.chat_data['password']}'")

        response = AdminAuth.generate_token(context)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Sucess on generating token")

            token = response.json()['data']['tokenAuth']['token']

            context.chat_data['token'] = token
            logger.debug(f"'token': '{context.chat_data['token']}'")

            update.message.reply_text('Autenticado(a) com sucesso!')
            create_admin(
                    email=context.chat_data['email'],
                    chat_id=chat_id,
                    token=token
                    )

            logger.debug(f"data: {context.chat_data}")
            context.chat_data.clear()

            return ConversationHandler.END

        else:
            logger.error("Failed generating token")
            update.message.reply_text(
                    'Falha na autenticação: email ou senha incorretos'
            )

            yes_keyboard = KeyboardButton('Sim')
            no_keyboard = KeyboardButton('Não')
            keyboard = [[yes_keyboard], [no_keyboard]]
            choice = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            update.message.reply_text('Deseja inseri-los novamente?', reply_markup=choice)

            return ADMIN_AUTH_REPEAT

    def repeat(update, context):
        """
        Repeat authentication interaction
        """
        choice = update.message.text

        if not ValidateForm.boolean_value(choice, update):
            return ADMIN_AUTH_REPEAT

        if choice == "Sim":
            logger.info("Replied 'yes'")
            update.message.reply_text('Ok! Por favor, informe seu email:')
            return ADMIN_AUTH_EMAIL
        else:
            update.message.reply_text('Ok!')
            logger.info("Replied 'no'")
            RegisterAdmin.end(update, context)

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """
        logger.info("Canceling admin authentication")

        update.message.reply_text('Autenticação cancelada!')

        logger.debug(f"data: {context.chat_data}")
        context.chat_data.clear()

        return ConversationHandler.END

    def generate_token(context):
        """
        Generate creator's token
        """
        logger.info("Generating admin token")
        query = """
            mutation tokenAuth($email: String!, $password: String!){
                tokenAuth(email: $email, password: $password){
                    token
                }
            }
            """

        variables = {
                'email': context.chat_data['email'],
                'password': context.chat_data['password'],
                }

        response = requests.post(PATH, json={'query':query, 'variables':variables})
        logger.debug(f"Response: {response.json()}")

        return response
