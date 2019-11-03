import logging
import requests
from settings import *
from telegram.ext import ConversationHandler

LOGGER = logging.getLogger(LOG_NAME)
CHAT = {}

class Feedback:

    @staticmethod
    def index(update, context):
        chat_id = update.message.chat_id

        LOGGER.info("Introducing feedback session")
        update.message.reply_text(
            "Ok. Digite a mensagem que deseja enviar como feedback para o nosso sistema:"
        )

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return FEEDBACK

    @staticmethod
    def store(update, context):
        chat_id = update.message.chat_id
        feedback = update.message.text

        CHAT[chat_id]['message'] = feedback
        LOGGER.debug(f"'feedback-message': '{CHAT[chat_id]['message']}'")

        LOGGER.info("Sending feedback to database")
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
            'message': CHAT[chat_id]['message'],
        }

        response = requests.post(PATH, json={'query':query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            update.message.reply_text('Seu feedback foi salvo no sistema, obrigado!')
            LOGGER.info("Feedback saved!")
        else:
            update.message.reply_text('Falha ao salvar no sistema!')
            LOGGER.error("Fail to save feedback")

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return ConversationHandler.END

    @staticmethod
    def end(update, context):
        chat_id = update.message.chat_id

        update.message.reply_text('Feedback cancelado!')
        LOGGER.info("Canceling feedback")

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return ConversationHandler.END
