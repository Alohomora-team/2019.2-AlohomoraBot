from auth import Auth
from register import Register
from settings import *
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import logging
import os

logging.basicConfig(format=FORMAT, datefmt=DATEFMT, level=LEVEL)

logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text('Olá, bem vindo(a) ao bot do Alohomora!')
    update.message.reply_text('Digite /cadastrar para fazer o cadastro de um morador')
    update.message.reply_text('Caso deseje fazer a autenticação por voz, digite /autenticar')


if __name__ == '__main__':

    token = TOKEN

    updater = Updater(token, use_context=True)

    logging.info("Iniciando Bot")

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


    updater.start_polling()

    updater.idle()
