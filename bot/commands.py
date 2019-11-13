from settings import LOG_NAME
import logging

logger = logging.getLogger(LOG_NAME)

chat = {}

class Commands:
    def morador(update, context):
        logger.info("Listing resident commands")
        update.message.reply_text("Como morador você pode:")
        update.message.reply_text("Autorizar a entrada de um visitante: /autorizar")
        update.message.reply_text("Cadastrar-se no sistema: /cadastrar")
        update.message.reply_text("Dar um feedback ao serviço: /feedback")
        

    def visitante(update, context):
        logger.info("Listing visitor commands")
        update.message.reply_text("Como visitante você pode:")
        update.message.reply_text("Realizar o pedido de uma visita: /visitar")
        update.message.reply_text("Dar um feedback ao serviço: /feedback")
