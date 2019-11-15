"""
Start program
"""

import logging
import os
from admin.notify_admin import NotifyAdmin
from admin.register_admin import RegisterAdmin
from commands import *
from feedback import Feedback
from resident.notify_resident import NotifyResident
from resident.register import Register
from resident.resident_auth import Auth
from settings import *
from telegram.ext import CallbackQueryHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from visitor.register_visitor import RegisterVisitor
from visitor.visit import Visit

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
    """
    Start interaction
    """
    logger.info(
        "Introducing the bot"
    )
    update.message.reply_text(
        'Olá, bem vindo(a) ao bot do Alohomora!'
    )
    update.message.reply_text(
        'Digite /morador para listar os comandos ligados aos moradores'
    )
    update.message.reply_text(
        'Digite /visitante para listar os comandos ligados aos visitantes'
    )
    update.message.reply_text(
        'Para dar um feedback pro nosso serviço, digite /feedback'
    )
    update.message.reply_text(
        'Para criar um novo administrador do sistema, digite /novoadmin'
    )

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
            CATCH_AUDIO_SPEAKING_NAME:[
                MessageHandler(Filters.voice, Register.catch_audio_speaking_name)
            ],
            CONFIRM_AUDIO_SPEAKING_NAME:[
                MessageHandler(Filters.text, Register.confirm_audio_speaking_name)
            ],
            VOICE_REGISTER:[MessageHandler(Filters.voice, Register.voice_register)],
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

    # Feedback
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('feedback', Feedback.index)],

        states={
            FEEDBACK: [MessageHandler(Filters.text, Feedback.store)],
            },

        fallbacks=[CommandHandler('cancelar', Feedback.end)]
        ))

    # Listing resident commands
    dp.add_handler(CommandHandler('morador', Commands.resident))

    # Listing visitor commands
    dp.add_handler(CommandHandler('visitante', Commands.visitor))

    # Register admin
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('novoadmin', RegisterAdmin.index)],

        states={
            EMAIL_AUTH_ADMIN: [MessageHandler(Filters.text, RegisterAdmin.auth_email)],
            PASSWORD_AUTH_ADMIN: [MessageHandler(Filters.text, RegisterAdmin.auth_password)],
            REPEAT_AUTH_ADMIN: [MessageHandler(Filters.text, RegisterAdmin.repeat_auth_admin)],
            ADMIN_REGISTER_EMAIL: [MessageHandler(Filters.text, RegisterAdmin.register_email)],
            ADMIN_REGISTER_PWD: [MessageHandler(Filters.text, RegisterAdmin.register_password)],
            },

        fallbacks=[CommandHandler('cancelar', RegisterAdmin.end)]
        ))

    # Admin
    dp.add_handler(CallbackQueryHandler(NotifyAdmin.approved, pattern='app'))
    dp.add_handler(CallbackQueryHandler(NotifyAdmin.rejected, pattern='rej'))

    # Resident
    dp.add_handler(CallbackQueryHandler(NotifyResident.authorized, pattern='aut'))
    dp.add_handler(CallbackQueryHandler(NotifyResident.refused, pattern='ref'))

    updater.start_polling()

    updater.idle()
