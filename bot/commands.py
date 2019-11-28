"""
Provides commands for the bot users
"""
import logging
from settings import LOG_NAME
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(LOG_NAME)

class Commands:
    """
    Provides commands for the bot users
    """
    def resident(update, context):
        """
        Display resident interations
        """
        logger.info("Sending message with resident interactions")
        chat_id = update.message.chat_id

        context.bot.send_message(
                chat_id=chat_id,
                text=Commands.resident_text(),
                reply_markup=Commands.resident_buttons(),
                parse_mode='Markdown'
                )

    def visitor(update, context):
        """
        Display visitor interations
        """
        logger.info("Sending message with visitor interactions")
        chat_id = update.message.chat_id

        context.bot.send_message(
                chat_id=chat_id,
                text=Commands.visitor_text(),
                reply_markup=Commands.visitor_buttons(),
                parse_mode='Markdown'
                )

    def admin(update, context):
        """
        Display admin interations
        """
        logger.info("Sending message with admin interactions")
        chat_id = update.message.chat_id

        context.bot.send_message(
                chat_id=chat_id,
                text=Commands.admin_text(),
                reply_markup=Commands.admin_buttons(),
                parse_mode='Markdown'
                )

    def resident_buttons():
        """
        Create resident buttons
        """
        keyboard = [
                [InlineKeyboardButton('Cadastrar', callback_data='r1')],
                [InlineKeyboardButton('Autenticar', callback_data='r2')],
                ]

        return InlineKeyboardMarkup(keyboard)

    def visitor_buttons():
        """
        Create visitor buttons
        """
        keyboard = [
                [InlineKeyboardButton('Cadastrar', callback_data='v1')],
                [InlineKeyboardButton('Fazer uma visitar', callback_data='v2')],
                ]

        return InlineKeyboardMarkup(keyboard)

    def admin_buttons():
        """
        Create admin buttons
        """
        keyboard = [
                [InlineKeyboardButton('Cadastrar novo admin', callback_data='a1')],
                [InlineKeyboardButton('Autenticar', callback_data='a2')],
                ]

        return InlineKeyboardMarkup(keyboard)

    def resident_text():
        """
        Resident interaction text
        """
        return """
*Estas são as interações disponíveis para moradores.

O que deseja fazer?*
        """
    def visitor_text():
        """
        Visitor interaction text
        """
        return """
*Estas são as interações disponíveis para visitantes.

O que deseja fazer?*
        """
    def admin_text():
        """
        Admin interaction text
        """
        return """
*Estas são as interações disponíveis para administradores.

O que deseja fazer?*
        """
