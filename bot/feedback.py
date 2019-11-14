"""
Feedback interactions
"""

import logging
import requests

from settings import *
from telegram.ext import ConversationHandler

logger = logging.getLogger(LOG_NAME)

chat = {}

class Feedback:
    """
    Class with feedback interactions
    """

    def index(update, context):
        """
        Start interaction
        """
        chat_id = update.message.chat_id

        logger.info("Introducing feedback session")
        update.message.reply_text(
            "Ok. Digite a mensagem que deseja enviar como feedback para o nosso sistema:"
        )

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return FEEDBACK

    def store(update, context):
        """
        Save feedback information
        """

        chat_id = update.message.chat_id
        feedback = update.message.text

        chat[chat_id]['message'] = feedback
        logger.debug(f"'feedback-message': '{chat[chat_id]['message']}'")

        logger.info("Sending feedback to database")
        query = """
        mutation createFeedback(
            $message: String!
            ){
            createFeedback(
                comment: $message,
            ){
                comment
            }
        }
        """

        variables = {
                'message': chat[chat_id]['message'],
                }

        response = requests.post(PATH, json={'query':query, 'variables':variables})
        logger.debug(f"Response: {response.json()}")

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            update.message.reply_text('Seu feedback foi salvo no sistema, obrigado!')
            logger.info("Feedback saved!")
        else:
            update.message.reply_text('Falha ao salvar no sistema!')
            logger.error("Fail to save feedback")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """
        chat_id = update.message.chat_id

        update.message.reply_text('Feedback cancelado!')
        logger.info("Canceling feedback")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END
