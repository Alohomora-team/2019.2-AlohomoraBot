import os
import json
import logging
import requests
import subprocess
import numpy

from checks import CheckAdmin
from settings import EMAIL_AUTH_ADMIN, PASSWORD_AUTH_ADMIN, REPEAT_AUTH_ADMIN, ADMIN_REGISTER_EMAIL, ADMIN_REGISTER_PASSWORD
from settings import PATH, LOG_NAME
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm



logger = logging.getLogger(LOG_NAME)

chat = {}

class RegisterAdmin:

    def index(update, context):
        logger.info("Introducing registration session")
        chat_id = update.message.chat_id

        update.message.reply_text('Para cadastrar um administrador, você precisa ser um!')
        update.message.reply_text('Preciso confirmar sua identidade.')
        update.message.reply_text('Por favor, digite seu email:')
        logger.info("Asking for email")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return EMAIL_AUTH_ADMIN

    def auth_email(update, context):
        chat_id = update.message.chat_id
        email = update.message.text

        if not ValidateForm.email(email, update):
            return EMAIL_AUTH_ADMIN

        chat[chat_id]['auth-email'] = email
        logger.debug(f"'auth-admin-email': '{chat[chat_id]['auth-email']}'")

        check = CheckAdmin.auth_email(chat, chat_id)

        if 'errors' not in check.keys():
            logger.error("Email exists in database")
            update.message.reply_text('Ok, email válido')

            logger.info("Requesting password")
            update.message.reply_text('Senha:')
            return PASSWORD_AUTH_ADMIN

        else:
            update.message.reply_text("Email não encontrado. Por favor, digite novamente")
            return EMAIL_AUTH_ADMIN

    def auth_password(update, context):
        chat_id = update.message.chat_id
        password = update.message.text

        chat[chat_id]['auth-password'] = password
        logger.debug(f"'auth-admin-password': '{chat[chat_id]['auth-password']}'")

        response = RegisterAdmin.generate_token(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Sucess on generating token")

            token = response.json()['data']['tokenAuth']['token']
            chat[chat_id]['token'] = token
            logger.debug(f"'auth-admin-token': '{chat[chat_id]['token']}'")

            update.message.reply_text('Muito bem! Podemos agora cadastrar um novo administrador.')
            update.message.reply_text('Por favor, informe o email do novo administrador:')

            logger.info("Requesting new admin's email")

            return ADMIN_REGISTER_EMAIL
        else:
            logger.error("Failed generating token")
            update.message.reply_text('Email ou senha incorretos. Não foi possível identificar o administrador.')
            
            yes_keyboard = KeyboardButton('Sim')
            no_keyboard = KeyboardButton('Não')
            keyboard = [[yes_keyboard], [no_keyboard]]
            choice = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            update.message.reply_text('Deseja inseri-los novamente?', reply_markup=choice)

            return REPEAT_AUTH_ADMIN

    def repeat_auth_admin(update, context):
        chat_id = update.message.chat_id
        choice = update.message.text

        if not ValidateForm.boolean_value(choice, update):
            return REPEAT_AUTH_ADMIN

        if choice == "Sim":
            logger.info("Replied 'yes'")
            update.message.reply_text('Ok! Por favor, informe seu email:')
            return EMAIL_AUTH_ADMIN
        else:
            update.message.reply_text('Ok!')
            logger.info("Replied 'no'")
            RegisterAdmin.end(update, context)

        return ConversationHandler.END

    def register_email(update, context):
        chat_id = update.message.chat_id
        email = update.message.text

        if not ValidateForm.email(email, update):
            return ADMIN_REGISTER_EMAIL
        
        chat[chat_id]['email'] = email
        logger.debug(f"'email': '{chat[chat_id]['email']}'")

        check = CheckAdmin.email(chat, chat_id)

        # if 'errors' not in check.keys():
        #     logger.error("Email already exists in database - asking again")
        #     update.message.reply_text('Já existe um administrador com este email, tente novamente:')
        #     return ADMIN_REGISTER_EMAIL

        logger.debug("Available email - proceed")

        update.message.reply_text('Senha:')
        logger.info("Asking for password")

        return ADMIN_REGISTER_PASSWORD

    def register_password(update, context):
        chat_id = update.message.chat_id
        password = update.message.text

        chat[chat_id]['password'] = password
        logger.debug(f"'password': '{chat[chat_id]['password']}'")

        response = RegisterAdmin.register_admin(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Admin registered in database")
            update.message.reply_text('Administrador cadastrado no sistema!')
        else:
            logger.error("Registration failed")
            update.message.reply_text('Falha ao cadastrar administrador no sistema!')

        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        chat[chat_id] = {}

        return ConversationHandler.END


    def end(update, context):
        logger.info("Canceling admin registration")
        chat_id = update.message.chat_id

        update.message.reply_text('Cadastro de admin cancelado!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

    def generate_token(chat_id):
        logger.info("Generating admin token")
        query = """
            mutation tokenAuth($email: String!, $password: String!){
                tokenAuth(email: $email, password: $password){
                    token
                }
            }
            """

        variables = {
                'email': chat[chat_id]['auth-email'],
                'password': chat[chat_id]['auth-password'],
                }
        response = requests.post(PATH, json={'query':query, 'variables':variables})
        logger.debug(f"Response: {response.json()}")

        return response

    def register_admin(chat_id):
        logger.info("Registering admin")
        query = """
        mutation createAdmin(
            $email: String!,
            $password: String!,
            ){
            createAdmin(
                email: $email,
                password: $password
            ){
                email
                creator {
                    email
                }
            }
        }
        """

        variables = {
                'email': chat[chat_id]['email'],
                'password': chat[chat_id]['password']
                }

        response = requests.post(PATH, headers={'Authorization': 'JWT %s' % chat[chat_id]['token']}, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response
