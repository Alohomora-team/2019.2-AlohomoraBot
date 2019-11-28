"""
Notification system for residents
"""

import logging
import requests

from db.schema import get_visitor_chat_id, get_residents_chat_ids, get_resident_apartment
from db.schema import get_resident_token
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from settings import PATH, LOG_NAME

logger = logging.getLogger(LOG_NAME)

messages = {}

class NotifyResident:
    """
    Notification system for residents
    """
    def send_notification(context, data):
        """
        Send notification to the resident who was request to visit
        """
        logger.info("Notifying residents about the visit")
        visitor_chat_id = get_visitor_chat_id(data['cpf'])
        logger.debug(f"\t| Visitor chat_id: {visitor_chat_id}")

        block = data['block']
        apartment = data['apartment']

        messages[visitor_chat_id] = {}
        logger.debug(f"\t| Dictionary with message_ids: {messages[visitor_chat_id]}")

        logger.info("Sending notification to all resident from the apartment")

        count = 0

        for chat_id in get_residents_chat_ids(block, apartment):
            logger.debug(f"\t| Resident chat_id: {chat_id}")

            response = NotifyResident.is_active(get_resident_token(chat_id))

            if 'errors' not in response.keys():
                if response['data']['me']['isActive']:

                    message = context.bot.send_message(
                            chat_id=chat_id,
                            text=NotifyResident.text(data),
                            reply_markup=NotifyResident.buttons(),
                            parse_mode='Markdown'
                            )

                    messages[visitor_chat_id][chat_id] = message.message_id
                    logger.debug(f"\t| Resident message_id: {message.message_id}")

                    count += 1

        if count == 0:
            context.bot.send_message(
                chat_id=visitor_chat_id,
                text="Não há moradores registrados nesse apartamento."
                )

        logger.debug(f"Dictionary with message_ids: {messages[visitor_chat_id]}")

    def authorized(update, context):
        """
        Authorize visitor entry
        """
        logger.info("Authorizing visit")
        query = update.callback_query

        cpf = [i for i in query.message.text.split() if i.isdigit()][0]
        logger.debug(f"\t| Visito cpf: {cpf}")

        visitor_chat_id = get_visitor_chat_id(cpf)
        logger.debug(f"\t| Visitor chat_id: {visitor_chat_id}")

        output = get_resident_apartment(query.message.chat_id)
        logger.debug(f"\t| Resident block, apartment: {output}")

        block = output[0]
        apartment = output[1]

        logger.info(
                "Notify the others residents that the visit has already been authorized"
                )
        for chat_id in get_residents_chat_ids(block, apartment):
            response = NotifyResident.is_active(get_resident_token(chat_id))

            if 'errors' not in response.keys():
                if response['data']['me']['isActive']:
                    message_id = messages[visitor_chat_id][chat_id]

                    if message_id != query.message.message_id:
                        logger.debug(f"\t| Resident chat_id: {chat_id}")
                        logger.debug(f"\t| Resident message_id: {message_id}")

                        context.bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=message_id,
                                text="Visitante autorizado por outro morador!"
                                )

        text = query.message.text
        text = text[31:]
        text = "*AUTORIZADO*" + text

        logger.info("Editing resident notification that authorized it")
        logger.debug(f"\t| Approval text:\n{text}\n")

        context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                parse_mode='Markdown'
                )

        logger.info(
                "Sending notification to the visitor informing that he has been authorized"
                )
        context.bot.send_message(
                chat_id=visitor_chat_id,
                text="Visita autorizada!"
                )

        messages[visitor_chat_id] = {}
        logger.debug(f"Dictionary with messages_id: {messages[visitor_chat_id]}")

    def refused(update, context):
        """
        Refuse visitor entry
        """
        logger.info("Refusing visit")
        query = update.callback_query

        cpf = [i for i in query.message.text.split() if i.isdigit()][0]
        logger.debug(f"\t| Visito cpf: {cpf}")

        visitor_chat_id = get_visitor_chat_id(cpf)
        logger.debug(f"\t| Visitor chat_id: {visitor_chat_id}")

        output = get_resident_apartment(query.message.chat_id)
        logger.debug(f"\t| Resident block, apartment: {output}")

        block = output[0]
        apartment = output[1]

        logger.info(
                "Notify the others residents that the visit has already been refused"
                )
        for chat_id in get_residents_chat_ids(block, apartment):
            response = NotifyResident.is_active(get_resident_token(chat_id))

            if 'errors' not in response.keys():
                if response['data']['me']['isActive']:
                    message_id = messages[visitor_chat_id][chat_id]

                    if message_id != query.message.message_id:
                        logger.debug(f"\t| Resident chat_id: {chat_id}")
                        logger.debug(f"\t| Resident message_id: {message_id}")

                        context.bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=message_id,
                                text="Visitante recusado por outro morador!"
                                )

        text = query.message.text
        text = text[31:]
        text = "*RECUSADO*" + text

        logger.info("Editing resident notification that refused it")
        logger.debug(f"\t| Refusal text:\n{text}\n")

        context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                parse_mode='Markdown'
                )

        logger.info(
                "Sending notification to the visitor informing that he has been refused"
                )
        context.bot.send_message(
                chat_id=visitor_chat_id,
                text="Visita recusada!"
                )

        messages[visitor_chat_id] = {}
        logger.debug(f"Dictionary with messages_id: {messages[visitor_chat_id]}")

    def text(data):
        """
        Resident notification message text
        """
        return f"""
*Visitante requisitando entrada:*

- *Nome:* {data['name']}
- *CPF:* {data['cpf']}
"""

    def buttons():
        """
        Create the notification buttons
        """
        keyboard = [
                [InlineKeyboardButton('Autorizar', callback_data='aut')],
                [InlineKeyboardButton('Recusar', callback_data='ref')],
                ]

        return InlineKeyboardMarkup(keyboard)

    def is_active(token):
        """Verify is a resident is active"""
        query = """
        query me{
            me{
                isActive
            }
        }
        """

        headers = {
                'Authorization': 'JWT %s' % token
                }

        response = requests.post(PATH, headers=headers, json={'query':query})
        print(response.json())

        return response.json()
