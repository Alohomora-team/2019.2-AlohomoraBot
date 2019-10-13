from telegram.ext import ConversationHandler

FEEDBACK = range(1)

PATH = "http://localhost:8000/graphql/"

feedback_chat = {}

class Feedback:

    def index(update, context):
        update.message.reply_text("Teste")

    def store(update, context):
        update.message.reply_text("Teste store")
