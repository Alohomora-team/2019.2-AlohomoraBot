"""
Provides commands for the bot users
"""
import logging
from settings import LOG_NAME

logger = logging.getLogger(LOG_NAME)

chat = {}

class Commands:
    """Provides commands for the bot users"""
    def resident(update, context):
        """Command to display resident's iterations"""
        logger.info("Listing resident commands")
        update.message.reply_text("Como morador você pode:")
        update.message.reply_text("Autorizar a entrada de um visitante: /autorizar")
        update.message.reply_text("Cadastrar-se no sistema: /cadastrar")


    def visitor(update, context):
        """Command to display visitor's iterations"""
        logger.info("Listing visitor commands")
        update.message.reply_text("Como visitante você pode:")
        update.message.reply_text("Realizar o pedido de uma visita: /visitar")
