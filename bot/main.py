from resident_control import Auth, HandleEntryVisitor
from register import Register
from register_visitor import RegisterVisitor
from feedback import Feedback
from visit import Visit
from settings import *
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

# Remove logs from APIs
logging.getLogger("telegram").setLevel(API_LOG_LEVEL)
logging.getLogger("JobQueue").setLevel(API_LOG_LEVEL)

# Logger
logging.basicConfig(format=FORMAT, datefmt=DATEFMT)
LOGGER = logging.getLogger(LOG_NAME)
LOGGER.setLevel(LOG_LEVEL)

# FileHandler
FILE_HANDLER = logging.FileHandler(FILE_NAME)
FILE_HANDLER.setLevel(LOG_LEVEL)
FILE_HANDLER.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFMT))
LOGGER.addHandler(FILE_HANDLER)

def start(update, context):
    LOGGER.info("Introducing the bot")
    update.message.reply_text('Olá, bem vindo(a) ao bot do Alohomora!')
    update.message.reply_text(
        'Caso deseje fazer uma solicitação de visita a algum morador, digite /visitar'
    )
    update.message.reply_text('Digite /cadastrar para fazer o cadastro de um morador')
    update.message.reply_text('Digite /autorizar para autorizar entrada de algum visitante')
    update.message.reply_text('Para dar um feedback pro nosso serviço, digite /feedback')


if __name__ == '__main__':
    UPDATER = Updater(TOKEN, use_context=True)

    LOGGER.info("Starting Bot")

    DP = UPDATER.dispatcher

    DP.add_handler(CommandHandler("start", start))

    # Registration
    DP.add_handler(ConversationHandler(
        entry_points=[CommandHandler('cadastrar', Register.index, pass_args=True)],

        states={
            NAME:[MessageHandler(Filters.text, Register.name)],
            PHONE:[MessageHandler(Filters.text | Filters.contact, Register.phone)],
            EMAIL:[MessageHandler(Filters.text, Register.email)],
            CPF:[MessageHandler(Filters.text, Register.cpf)],
            BLOCK:[MessageHandler(Filters.text, Register.block)],
            APARTMENT:[MessageHandler(Filters.text, Register.apartment)],
            CATCH_AUDIO_SPEAKING_NAME:[
                MessageHandler(Filters.voice, Register.catch_audio_speaking_name)
            ],
            CONFIRM_AUDIO_SPEAKING_NAME:[
                MessageHandler(Filters.text, Register.confirm_audio_speaking_name)
            ],
            VOICE_REGISTER: [MessageHandler(Filters.voice, Register.voice_register)],
            REPEAT_VOICE:[MessageHandler(Filters.text, Register.repeat_voice)]
            },

        fallbacks=[CommandHandler('cancelar', Register.end)]
        ))

    # Handle visitor (register resident and register entry)
    DP.add_handler(ConversationHandler(
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

    # Resident control
    DP.add_handler(ConversationHandler(
        entry_points=[CommandHandler('autorizar', Auth.index)],

        states={
            CPF_AUTH:[MessageHandler(Filters.text, Auth.cpf)],
            VOICE_AUTH: [MessageHandler(Filters.voice, Auth.voice)],
            SHOW_VISITORS_PENDING: [MessageHandler(Filters.text, HandleEntryVisitor.index)]
            },

        fallbacks=[CommandHandler('cancelar', Auth.end)]
        ))

    # Feedback
    DP.add_handler(ConversationHandler(
        entry_points=[CommandHandler('feedback', Feedback.index)],

        states={
            FEEDBACK: [MessageHandler(Filters.text, Feedback.store)],
            },

        fallbacks=[CommandHandler('cancelar', Feedback.end)]
        ))


    UPDATER.start_polling()

    UPDATER.idle()
