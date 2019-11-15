"""
Interactions to register an admin
"""

import json
import logging
import os
import subprocess
import numpy
import requests

from checks import CheckAdmin
from settings import ADMIN_REGISTER_EMAIL, ADMIN_REGISTER_PWD
from settings import ADMIN_AUTH_EMAIL, ADMIN_AUTH_PWD, ADMIN_AUTH_REPEAT
from settings import PATH, LOG_NAME
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm


logger = logging.getLogger(LOG_NAME)

chat = {}

class RegisterAdmin:
    """
    Register an admin
    """

    def index(update, context):
        """
        Start the conversation
        """
        logger.info("Introducing registration session")
        chat_id = update.message.chat_id

        update.message.reply_text('Email:')
        logger.info("Asking for email")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ADMIN_REGISTER_EMAIL

    def email(update, context):
        """
        Get new admin's email
        """
        chat_id = update.message.chat_id
        email = update.message.text

        if not ValidateForm.email(email, update):
            return ADMIN_REGISTER_EMAIL

        chat[chat_id]['email'] = email
        logger.debug(f"'email': '{chat[chat_id]['email']}'")

        check = CheckAdmin.email(chat, chat_id)

        if 'errors' not in check.keys():
            logger.error("Email already exists in database - asking again")
            update.message.reply_text(
                    'Já existe um administrador com este email, tente novamente:'
                    )
            return ADMIN_REGISTER_EMAIL

        logger.debug("Available email - proceed")

        update.message.reply_text('Senha:')
        logger.info("Asking for password")

        return ADMIN_REGISTER_PWD

    def password(update, context):
        """
        Get new admin's password
        """
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
        """
        Cancel interaction
        """
        logger.info("Canceling admin registration")
        chat_id = update.message.chat_id

        update.message.reply_text('Cadastro de admin cancelado!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

    def generate_token(chat_id):
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
                'email': chat[chat_id]['auth-email'],
                'password': chat[chat_id]['auth-password'],
                }
        response = requests.post(PATH, json={'query':query, 'variables':variables})
        logger.debug(f"Response: {response.json()}")

        return response

    def register_admin(chat_id):
        """
        Register an admin
        """
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

        response = requests.post(PATH,
                                headers={'Authorization': 'JWT %s' % chat[chat_id]['token']},
                                json={'query':query,
                                'variables':variables}
                                )

        logger.debug(f"Response: {response.json()}")

        return response
