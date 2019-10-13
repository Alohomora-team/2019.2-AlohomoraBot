from telegram.ext import ConversationHandler
import requests

FEEDBACK = range(1)

PATH = "http://localhost:8000/graphql/"

chat = {}

class Feedback:

    def index(update, context):
        chat_id = update.message.chat_id

        update.message.reply_text("Ok. Digite a mensagem que deseja enviar como feedback para o nosso sistema.")
        update.message.reply_text("Feedback:")

        chat[chat_id] = {} 

        return FEEDBACK

    def store(update, context):
        chat_id = update.message.chat_id
        feedback = update.message.text

        chat[chat_id]['message'] = feedback
        
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

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            update.message.reply_text('Seu feedback foi salvo no sistema, obrigado!')
        else:
            update.message.reply_text('Falha ao salvar no sistema!')

        chat[chat_id] = {}

        return ConversationHandler.END

    def end(update, context):
        chat_id = update.message.chat_id

        update.message.reply_text('Feedback cancelado!')

        chat[chat_id] = {}

        return ConversationHandler.END
