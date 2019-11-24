"""
Start program
"""

import logging
import os
from admin.notify_admin import NotifyAdmin
from admin.register_admin import RegisterAdmin
from admin.admin_auth import AdminAuth
from commands import *
from feedback import Feedback
from resident.notify_resident import NotifyResident
from resident.register_resident import RegisterResident
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

    # Resident register
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('cadastrar', RegisterResident.index)],

        states={
            NAME:[MessageHandler(Filters.text, RegisterResident.name)],
            PHONE:[MessageHandler(Filters.text | Filters.contact, RegisterResident.phone)],
            EMAIL:[MessageHandler(Filters.text, RegisterResident.email)],
            CPF:[MessageHandler(Filters.text, RegisterResident.cpf)],
            APARTMENT:[MessageHandler(Filters.text, RegisterResident.apartment)],
            BLOCK:[MessageHandler(Filters.text, RegisterResident.block)],
            PASSWORD: [MessageHandler(Filters.text, RegisterResident.password)],
            VOICE_REGISTER:[MessageHandler(Filters.voice, RegisterResident.voice_register)],
            REPEAT_VOICE:[MessageHandler(Filters.text, RegisterResident.repeat_voice)]
            },

        fallbacks=[CommandHandler('cancelar', RegisterResident.end)]
        ))

    # Resident authentication

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('autenticar', ResidentAuth.index)],

        states={
            CHOOSE_AUTH:[MessageHandler(Filters.text, ResidentAuth.choose_auth)],
            VOICE_AUTH:[MessageHandler(Filters.text, ResidentAuth.voice)],
            PASSWORD_AUTH:[MessageHandler(Filters.text, ResidentAuth.password)],
            },

        fallbacks=[CommandHandler('cancelar', ResidentAuth.end)]
        ))

    # Visitor register
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('cadastrar_visitante', RegisterVisitor.index)],

        states={
            VISITOR_REGISTER_NAME:[MessageHandler(Filters.text, RegisterVisitor.name)],
            VISITOR_REGISTER_CPF:[MessageHandler(Filters.text, RegisterVisitor.cpf)],
            },

        fallbacks=[CommandHandler('cancelar', RegisterVisitor.end)]
        ))

    # Visit
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('visitar', Visit.index)],

        states={
            VISIT_BLOCK:[MessageHandler(Filters.text, Visit.block)],
            VISIT_APARTMENT:[MessageHandler(Filters.text, Visit.apartment)],
            },

        fallbacks=[CommandHandler('cancelar', Visit.end)]
        ))

    # Admin register
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('criar_admin', RegisterAdmin.index)],

        states={
            ADMIN_REGISTER_EMAIL: [MessageHandler(Filters.text, RegisterAdmin.email)],
            ADMIN_REGISTER_PWD: [MessageHandler(Filters.text, RegisterAdmin.password)],
            },

        fallbacks=[CommandHandler('cancelar', RegisterAdmin.end)]
        ))

    # Admin authentication
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('autenticar_admin', AdminAuth.index)],

        states={
            ADMIN_AUTH_EMAIL: [MessageHandler(Filters.text, AdminAuth.email)],
            ADMIN_AUTH_PWD: [MessageHandler(Filters.text, AdminAuth.password)],
            ADMIN_AUTH_REPEAT: [MessageHandler(Filters.text, AdminAuth.repeat)],
            },

        fallbacks=[CommandHandler('cancelar', AdminAuth.end)]
        ))
    # Admin notification
    dp.add_handler(CallbackQueryHandler(NotifyAdmin.approved, pattern='app'))
    dp.add_handler(CallbackQueryHandler(NotifyAdmin.rejected, pattern='rej'))

    # Resident notification
    dp.add_handler(CallbackQueryHandler(NotifyResident.authorized, pattern='aut'))
    dp.add_handler(CallbackQueryHandler(NotifyResident.refused, pattern='ref'))

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

    updater.start_polling()

    updater.idle()
