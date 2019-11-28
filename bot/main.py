"""
Start program
"""

import logging
import os

from commands import Commands
from admin.admin_auth import AdminAuth
from admin.notify_admin import NotifyAdmin
from admin.register_admin import RegisterAdmin
from feedback import Feedback
from resident.notify_resident import NotifyResident
from resident.register_resident import RegisterResident
from resident.resident_auth import ResidentAuth
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
    logger.info("Introducing the bot")
    chat_id = update.message.chat_id

    context.bot.send_message(
            chat_id=chat_id,
            parse_mode='Markdown',
            text=
            """
Olá, bem vindo(a) ao bot do *Alohomora*!

*Comandos*
/morador - interações para moradores
/visitante - interações para visitante
/admin - interações para administradores

Para dar um _feedback_ pro nosso serviço, digite /feedback
"""
    )


if __name__ == '__main__':

    token = TOKEN
    port = int(os.environ.get('PORT', '8443'))

    updater = Updater(token, use_context=True)

    logger.info("Starting Bot")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    # Resident register
    dp.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(RegisterResident.index, pattern='r1')],

        states={
            NAME:[MessageHandler(Filters.text, RegisterResident.name)],
            PHONE:[MessageHandler(Filters.text | Filters.contact, RegisterResident.phone)],
            EMAIL:[MessageHandler(Filters.text, RegisterResident.email)],
            CPF:[MessageHandler(Filters.text, RegisterResident.cpf)],
            BLOCK:[MessageHandler(Filters.text, RegisterResident.block)],
            APARTMENT:[MessageHandler(Filters.text, RegisterResident.apartment)],
            VOICE_REGISTER:[MessageHandler(Filters.voice, RegisterResident.voice_register)],
            REPEAT_VOICE:[MessageHandler(Filters.text, RegisterResident.repeat_voice)],
            PASSWORD: [MessageHandler(Filters.text, RegisterResident.password)]
            },

        fallbacks=[CommandHandler('cancelar', RegisterResident.end)]
        ))

    # Resident authentication
    dp.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(ResidentAuth.index, pattern='r2')],

        states={
            CHOOSE_AUTH:[MessageHandler(Filters.text, ResidentAuth.choose_auth)],
            VOICE_AUTH:[MessageHandler(Filters.voice, ResidentAuth.voice)],
            PASSWORD_AUTH:[MessageHandler(Filters.text, ResidentAuth.password)],
            },

        fallbacks=[CommandHandler('cancelar', ResidentAuth.end)]
        ))

    # Visitor register
    dp.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(RegisterVisitor.index, pattern='v1')],

        states={
            VISITOR_REGISTER_NAME:[MessageHandler(Filters.text, RegisterVisitor.name)],
            VISITOR_REGISTER_CPF:[MessageHandler(Filters.text, RegisterVisitor.cpf)],
            },

        fallbacks=[CommandHandler('cancelar', RegisterVisitor.end)]
        ))

    # Visit
    dp.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(Visit.index, pattern='v2')],

        states={
            VISIT_BLOCK:[MessageHandler(Filters.text, Visit.block)],
            VISIT_APARTMENT:[MessageHandler(Filters.text, Visit.apartment)],
            },

        fallbacks=[CommandHandler('cancelar', Visit.end)]
        ))

    # Admin register
    dp.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(RegisterAdmin.index, pattern='a1')],

        states={
            ADMIN_REGISTER_EMAIL: [MessageHandler(Filters.text, RegisterAdmin.email)],
            ADMIN_REGISTER_PWD: [MessageHandler(Filters.text, RegisterAdmin.password)],
            },

        fallbacks=[CommandHandler('cancelar', RegisterAdmin.end)]
        ))

    # Admin authentication
    dp.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(AdminAuth.index, pattern='a2')],

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

    # Listing admin commands
    dp.add_handler(CommandHandler('admin', Commands.admin))

    if os.environ['DEPLOY'] == 'True':
        updater.start_webhook(listen="0.0.0.0",
                        port=port,
                        url_path=token)

        updater.bot.set_webhook(os.environ['URL'] + token)

    elif os.environ['DEPLOY'] == 'False':
        updater.start_polling()

    updater.idle()
