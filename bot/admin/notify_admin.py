"""
Provides a notification system for the bot
"""

import logging

from admin.admin import Admin
from db.schema import get_all_admins_chat_ids, get_resident_chat_id, delete_resident
from settings import LOG_NAME
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(LOG_NAME)

messages = {}

class NotifyAdmin:
    """
    Notification system for admins
    """
    def send_message(context, data):
        """
        Send message to all admins registered in database
        """

        logger.info("Notifying admins that a resident request a approval")

        resident_chat_id = get_resident_chat_id(data['cpf'])
        logger.debug(f"\t| Resident chat_id: {resident_chat_id}")

        messages[resident_chat_id] = {}
        logger.debug(f"\t| Dictionary with message_ids: {messages[resident_chat_id]}")

        logger.info("Sending notification to all admins in database")

        count = 0

        for chat_id in get_all_admins_chat_ids():
            logger.debug(f"\t| Admin chat_id: {chat_id}")

            message = context.bot.send_message(
                    chat_id=chat_id,
                    text=NotifyAdmin.text(data),
                    reply_markup=NotifyAdmin.buttons(),
                    parse_mode='Markdown'
                    )

            messages[resident_chat_id][chat_id] = message.message_id
            logger.debug(f"\t| Admin message_id: {message.message_id}")

            count += 1

        if count == 0:
            context.bot.send_message(
                chat_id=resident_chat_id,
                text="Não há administradores registrados no momento."
                )

        logger.debug(f"Dictionary with message_ids: {messages[resident_chat_id]}")

    def approved(update, context):
        """
        Activate resident in database and notify him
        """

        logger.info("Approving resident registration")
        query = update.callback_query

        cpf = [i for i in query.message.text.split('-')[-3].split() if i.isdigit()][0]
        logger.debug(f"\t| Resident cpf: {cpf}")

        resident_chat_id = get_resident_chat_id(cpf)
        logger.debug(f"\t| Resident chat_id: {resident_chat_id}")

        logger.info("Activating resident in database")

        email = query.message.text.split('-')[-4].split()[1]
        logger.debug(f"\t| Resident email: {email}")

        response = Admin.activate_resident(email)
        logger.debug(f"\t| Response: {response}")

        if 'errors' not in response.keys():

            logger.info(
                    "Notify the others admins that the resident has already been approved")

            for chat_id in get_all_admins_chat_ids():

                message_id = messages[resident_chat_id][chat_id]

                if message_id != query.message.message_id:
                    logger.debug(f"\t| Admin chat_id: {chat_id}")
                    logger.debug(f"\t| Admin message_id: {message_id}")

                    context.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text="Morador aprovado por outro administrador!"
                            )

            text = query.message.text
            text = text[30:]
            text = "*APROVADO*" + text

            logger.info("Editing admin notification that approved it")
            logger.debug(f"\t| Approval text:\n{text}\n")

            context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=text,
                    parse_mode='Markdown'
                    )

            logger.info(
                    "Sending notification to the resident informing that he has been approved")
            context.bot.send_message(
                    chat_id=resident_chat_id,
                    text="Cadastro aprovado!"
                    )

            messages[resident_chat_id] = {}
            logger.debug(f"Dictionary with messages_id: {messages[resident_chat_id]}")

        else:
            context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="Ocorrou um problema durante a operação."
                    )

    def rejected(update, context):
        """
        Delete resident from database and notify him
        """

        logger.info("Rejecting resident registration")
        query = update.callback_query

        cpf = [i for i in query.message.text.split('-')[-3].split() if i.isdigit()][0]
        logger.debug(f"\t| Resident cpf: {cpf}")

        resident_chat_id = get_resident_chat_id(cpf)
        logger.debug(f"\t| Resident chat_id: {resident_chat_id}")

        logger.info("Deleting resident in database")

        email = query.message.text.split('-')[-4].split()[1]
        logger.debug(f"\t| Resident email: {email}")

        response = Admin.delete_resident(email)
        logger.debug(f"\t| Response: {response}")

        if 'errors' not in response.keys():
            delete_resident(cpf)

            logger.info(
                    "Notify the others admins that the resident has already been rejected")

            for chat_id in get_all_admins_chat_ids():

                message_id = messages[resident_chat_id][chat_id]

                if message_id != query.message.message_id:
                    logger.debug(f"\t| Admin chat_id: {chat_id}")
                    logger.debug(f"\t| Admin message_id: {message_id}")

                    context.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text="Morador rejeitado por outro administrador!"
                            )

            text = query.message.text
            text = text[30:]
            text = "*REJEITADO*" + text

            logger.info("Editing admin notification that rejected it")
            logger.debug(f"\t| Rejection text:\n{text}\n")

            context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=text,
                    parse_mode='Markdown'
                    )

            logger.info(
                    "Sending notification to the resident informing that he has been rejected")
            context.bot.send_message(
                    chat_id=resident_chat_id,
                    text="Cadastro rejeitado."
                    )

            messages[resident_chat_id] = {}
            logger.debug(f"Dictionary with messages_id: {messages[resident_chat_id]}")

        else:
            context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="Ocorrou um problema durante a operação."
                    )

    def text(data):
        """Return admin notification message text"""
        return f"""
        *Morador requisitando cadastro:*

- *Nome:*  {data['name']}
- *Telefone:*  {data['phone']}
- *Email:*  {data['email']}
- *CPF:*  {data['cpf']}
- *Bloco:*  {data['block']}
- *Apartamento:*  {data['apartment']}
        """

    def buttons():
        """Create the notification buttons"""
        keyboard = [
               [InlineKeyboardButton('Aprovar', callback_data='app')],
               [InlineKeyboardButton('Rejeitar', callback_data='rej')],
               ]

        return InlineKeyboardMarkup(keyboard)
