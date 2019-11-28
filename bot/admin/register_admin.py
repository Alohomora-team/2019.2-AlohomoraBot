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
from db.schema import admin_exists, get_admin_token
from settings import ADMIN_REGISTER_EMAIL, ADMIN_REGISTER_PWD
from settings import PATH, LOG_NAME
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm

logger = logging.getLogger(LOG_NAME)

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

        if not admin_exists(chat_id):
            logger.info("Unauthenticated admin - ending")
            update.message.reply_text(
                    'Você precisa estar autenticado para fazer este procedimento!'
                    )
            return ConversationHandler.END

        update.message.reply_text('Email:')
        logger.info("Asking for email")

        logger.debug("data: {context.chat_data}")

        return ADMIN_REGISTER_EMAIL

    def email(update, context):
        """
        Get new admin's email
        """
        email = update.message.text

        if not ValidateForm.email(email, update):
            return ADMIN_REGISTER_EMAIL

        context.chat_data['email'] = email
        logger.debug(f"'email': '{context.chat_data['email']}'")

        check = CheckAdmin.email(email)

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

        context.chat_data['password'] = password
        logger.debug(f"'password': '{context.chat_data['password']}'")

        response = RegisterAdmin.register_admin(context, chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Admin registered in database")
            update.message.reply_text('Administrador cadastrado no sistema!')
        else:
            logger.error("Registration failed")
            update.message.reply_text('Falha ao cadastrar administrador no sistema!')

        logger.debug(f"data: {context.chat_data}")
        context.chat_data.clear()

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """
        logger.info("Canceling admin registration")

        update.message.reply_text('Cadastro de admin cancelado!')

        logger.debug(f"data: {context.chat_data}")
        context.chat_data.clear()

        return ConversationHandler.END

    def register_admin(context, chat_id):
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
                'email': context.chat_data['email'],
                'password': context.chat_data['password']
                }

        response = requests.post(PATH,
                                headers={'Authorization': 'JWT %s' % get_admin_token(chat_id)},
                                json={'query':query,
                                'variables':variables}
                                )

        logger.debug(f"Response: {response.json()}")

        return response
