from commands import *
from resident_control import Auth, HandleEntryVisitor
from register import Register
from register_visitor import RegisterVisitor
from feedback import Feedback
from visit import Visit
from settings import *
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import logging
import os

# Remove logs from APIs
logging.getLogger("telegram").setLevel(API_LOG_LEVEL)
logging.getLogger("JobQueue").setLevel(API_LOG_LEVEL)

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
    update.message.reply_text('Caso você seja um morador, digite /morador para listar os comandos ligados aos moradores')
    update.message.reply_text('Caso você seja um visitante, digite /visitante para listar os comandos ligados aos visitantes')
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

    # Handle visitor (register resident and register entry)
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('visitar', Visit.index, pass_args=True)],

        states={
            VERIFY_REGISTRATION:[MessageHandler(Filters.text, Visit.verify_registration)],
            VISITOR_REGISTER_NAME:[MessageHandler(Filters.text, RegisterVisitor.name)],
            VISITOR_REGISTER_CPF:[MessageHandler(Filters.text, RegisterVisitor.cpf)],
            VISITOR_CPF:[MessageHandler(Filters.text, Visit.cpf)],
            VISITOR_BLOCK:[MessageHandler(Filters.text, Visit.block)],
            VISITOR_APARTMENT:[MessageHandler(Filters.text, Visit.apartment)],
            CREATE_VISITOR_ENTRY:[MessageHandler(Filters.text, Visit.create_entry)],
            },

        fallbacks=[CommandHandler('cancelar', Visit.end)]
        ))

    # Resident control (manage apartment entries )
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('autorizar', Auth.index)],

        states={
            CPF_AUTH:[MessageHandler(Filters.text, Auth.cpf)],
            VOICE_AUTH: [MessageHandler(Filters.voice, Auth.voice)],
            HANDLE_VISITORS_PENDING: [MessageHandler(Filters.text, HandleEntryVisitor.index)]
            },

        fallbacks=[CommandHandler('cancelar', HandleEntryVisitor.end)]
        ))

    # Feedback
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('feedback', Feedback.index)],

        states={
            FEEDBACK: [MessageHandler(Filters.text, Feedback.store)],
            },

        fallbacks=[CommandHandler('cancelar', Feedback.end)]
        ))
    
    dp.add_handler(CommandHandler('morador', Commands.resident))

    dp.add_handler(CommandHandler('visitante', Commands.visitor))

    updater.start_polling()

    updater.idle()
