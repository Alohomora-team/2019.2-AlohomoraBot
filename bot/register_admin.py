from checks import CheckAdmin
from settings import EMAIL_AUTH_ADMIN, PASSWORD_AUTH_ADMIN
from settings import PATH, LOG_NAME
from telegram.ext import ConversationHandler
from validator import ValidateForm
import json
import logging
import numpy
import os
import requests
import subprocess


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

    def email(update, context):
        chat_id = update.message.chat_id
        email = update.message.text

        if not ValidateForm.email(email, update):
            return EMAIL_AUTH_ADMIN

        chat[chat_id]['email'] = email
        logger.debug(f"'auth-admin-email': '{chat[chat_id]['email']}'")

        check = CheckAdmin.email(chat, chat_id)

        if 'errors' not in check.keys():
            logger.error("Email exists in database")
            update.message.reply_text('Ok, email válido')

            logger.info("Requesting password")
            update.message.reply_text('Senha:')
            return PASSWORD_AUTH_ADMIN

        else:
            update.message.reply_text("Email não encontrado. Por favor, digite novamente")
            return EMAIL_AUTH_ADMIN

    def password(update, context):
        chat_id = update.message.chat_id
        password = update.message.text

        chat[chat_id]['password'] = password
        logger.debug(f"'auth-admin-password': '{chat[chat_id]['password']}'")

        response = RegisterAdmin.generate_token(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Sucess on generating token")
            update.message.reply_text('Muito bem! Podemos agora cadastrar um novo administrador')
        else:
            logger.error("Failed generating token")
            update.message.reply_text('Email ou senha incorretos. Não foi possível identificar o administrador.')
            update.message.reply_text('Deseja inseri-los novamente?')

        token = response.json()['data']['tokenAuth']['token']

        chat[chat_id]['token'] = token
        logger.debug(f"'auth-admin-token': '{chat[chat_id]['token']}'")

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
                'email': chat[chat_id]['email'],
                'password': chat[chat_id]['password'],
                }
        
        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response

        
