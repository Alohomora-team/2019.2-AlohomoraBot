from auth import Auth
from register import Register
from feedback import Feedback
from settings import *
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import logging
import os

# Remove logs from APIs
logging.getLogger("telegram").setLevel(logging.CRITICAL)
logging.getLogger("JobQueue").setLevel(logging.CRITICAL)

# Logger
logging.basicConfig(format=FORMAT, datefmt=DATEFMT)
logger = logging.getLogger(LOG_NAME)
logger.setLevel(LOG_LEVEL)

# FileHandler
file_handler = logging.FileHandler(FILE_NAME)
file_handler.setLevel(LOG_LEVEL)
f_format = logging.Formatter(FORMAT, datefmt=DATEFMT)
file_handler.setFormatter(f_format)
logger.addHandler(file_handler)

def start(update, context):
    logger.info("Introducing the bot")
    update.message.reply_text('Olá, bem vindo(a) ao bot do Alohomora!')
    update.message.reply_text('Digite /cadastrar para fazer o cadastro de um morador')
    update.message.reply_text('Caso queira fazer a autenticação por voz, digite /autenticar')
    update.message.reply_text('Para dar um feedback pro nosso serviço, digite /feedback')


if __name__ == '__main__':

    token = TOKEN

    updater = Updater(token, use_context=True)

    logger.info("Starting Bot")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    # Registration
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('cadastrar', Register.index, pass_args=True)],

        states={
            NAME:[MessageHandler(Filters.text, Register.name)],
            PHONE:[MessageHandler(Filters.text | Filters.contact, Register.phone)],
            EMAIL:[MessageHandler(Filters.text, Register.email)],
            CPF:[MessageHandler(Filters.text, Register.cpf)],
            APARTMENT:[MessageHandler(Filters.text, Register.apartment)],
            BLOCK:[MessageHandler(Filters.text, Register.block)],
            VOICE_REGISTER: [MessageHandler(Filters.voice, Register.voice_register)],
            REPEAT_VOICE:[MessageHandler(Filters.text, Register.repeat_voice)]
            },

        fallbacks=[CommandHandler('cancelar', Register.end)]
        ))

    # Authentication
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('autenticar', Auth.index)],

        states={
            CPF_AUTH:[MessageHandler(Filters.text, Auth.cpf)],
            VOICE_AUTH: [MessageHandler(Filters.voice, Auth.voice)]
            },

        fallbacks=[CommandHandler('cancelar', Auth.end)]
        ))

    # Feedback
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('feedback', Feedback.index)],

        states={
            FEEDBACK: [MessageHandler(Filters.text, Feedback.store)],
            },

        fallbacks=[CommandHandler('cancelar', Feedback.end)]
        ))


    updater.start_polling()

    updater.idle()
