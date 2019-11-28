"""
Interactions for user feedback
"""

import logging
import requests

from settings import PATH, LOG_NAME, API_TOKEN
from settings import FEEDBACK
from telegram.ext import ConversationHandler

logger = logging.getLogger(LOG_NAME)

class Feedback:
    """
    Save feedback from the user
    """

    def index(update, context):
        """
        Start interaction
        """
        logger.info("Introducing feedback session")

        update.message.reply_text(
            "Digite a mensagem que deseja enviar como feedback para o nosso sistema:"
        )

        return FEEDBACK

    def store(update, context):
        """
        Save a feedback in database
        """
        feedback = update.message.text

        logger.debug(f"'feedback': '{feedback}'")

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
                'message': feedback,
                }

        response = requests.post(PATH, json={'query':query, 'variables':variables})
        logger.debug(f"Response: {response.json()}")

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            update.message.reply_text('Seu feedback foi salvo no sistema, obrigado!')
            logger.info("Feedback saved!")
        else:
            update.message.reply_text('Falha ao salvar no sistema!')
            logger.error("Fail to save feedback")

        return ConversationHandler.END

    def end(update, context):
        """
        Stop interaction
        """
        update.message.reply_text('Feedback cancelado!')
        logger.info("Canceling feedback")

        return ConversationHandler.END
