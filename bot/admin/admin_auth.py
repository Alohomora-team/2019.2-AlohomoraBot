"""
Authenticate a admin
"""
import logging
from db.schema import admin_exists, create_admin
from checks import CheckAdmin
from settings import LOG_NAME
from settings import ADMIN_AUTH_EMAIL, ADMIN_AUTH_PWD, ADMIN_AUTH_REPEAT

chat = {}

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
        chat_id = update.message.chat_id

        if admin_exists(chat_id):
            update.message.reply_text('Você já está autenticado!')
            return ConversationHandler.END

        update.message.reply_text('Por favor, digite seu email:')
        logger.info("Asking for email")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ADMIN_AUTH_EMAIL

    def email(update, context):
        """
        Get email to authenticate admin
        """
        chat_id = update.message.chat_id
        email = update.message.text

        if not ValidateForm.email(email, update):
            return ADMIN_AUTH_EMAIL

        chat[chat_id]['email'] = email
        logger.debug(f"'email': '{chat[chat_id]['email']}'")

        check = CheckAdmin.auth_email(chat, chat_id)

        if 'errors' not in check.keys():
            logger.error("Email exists in database")
            update.message.reply_text('Ok, email válido')

            logger.info("Requesting password")
            update.message.reply_text('Senha:')
            return ADMIN_AUTH_PWD

        else:
            update.message.reply_text("Email não encontrado. Por favor, digite novamente")
            return ADMIN_AUTH_EMAIL

    def password(update, context):
        """
        Get password to authenticate admin
        """
        chat_id = update.message.chat_id
        password = update.message.text

        chat[chat_id]['password'] = password
        logger.debug(f"'password': '{chat[chat_id]['password']}'")

        response = RegisterAdmin.generate_token(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Sucess on generating token")

            token = response.json()['data']['tokenAuth']['token']
            chat[chat_id]['token'] = token
            logger.debug(f"'token': '{chat[chat_id]['token']}'")

            update.message.reply_text('Muito bem! Autenticado com sucesso.')
            create_admin(
                    email=chat[chat_id]['email'],
                    chat_id=chat_id
                    )

            return ConversationHandler.END

        else:
            logger.error("Failed generating token")
            update.message.reply_text(
                'Email ou senha incorretos. Não foi possível identificar o administrador.'
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
        chat_id = update.message.chat_id
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
        chat_id = update.message.chat_id

        update.message.reply_text('Autenticação cancelada!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

