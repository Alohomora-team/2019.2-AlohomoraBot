"""Notification system for residents"""
from db.schema import get_visitor_chat_id, get_residents_chat_ids, get_resident_apartment
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

MESSAGES = {}

class NotifyResident:
    """Notification system for residents"""
    def send_notification(context, data):
        """Send notification to the resident who was request to visit"""

        visitor_chat_id = get_visitor_chat_id(data['cpf'])
        block = data['block']
        apartment = data['apartment']

        MESSAGES[visitor_chat_id] = {}

        for chat_id in get_residents_chat_ids(block, apartment):
            message = context.bot.send_message(
                    chat_id=chat_id,
                    text=NotifyResident.text(data),
                    reply_markup=NotifyResident.buttons(),
                    parse_mode='Markdown'
                    )

            MESSAGES[visitor_chat_id][chat_id] = message.message_id

    def authorized(update, context):
        """Authorize visitor entry"""
        query = update.callback_query

        cpf = [i for i in query.message.text.split() if i.isdigit()][0]

        visitor_chat_id = get_visitor_chat_id(cpf)

        output = get_resident_apartment(query.message.chat_id)
        block = output[0]
        apartment = output[1]

        for chat_id in get_residents_chat_ids(block, apartment):
            message_id = MESSAGES[visitor_chat_id][chat_id]

            if message_id != query.message.message_id:
                context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="Visitante autorizado por outro morador!"
                        )

        text = query.message.text
        text = text[31:]
        text = "*AUTORIZADO*" + text

        context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                parse_mode='Markdown'
                )

        context.bot.send_message(
                chat_id=visitor_chat_id,
                text="Visita autorizada!"
                )

        MESSAGES[visitor_chat_id] = {}

    def refused(update, context):
        """Refuse visitor entry"""
        query = update.callback_query

        cpf = [i for i in query.message.text.split() if i.isdigit()][0]

        visitor_chat_id = get_visitor_chat_id(cpf)

        output = get_resident_apartment(query.message.chat_id)
        block = output[0]
        apartment = output[1]

        for chat_id in get_residents_chat_ids(block, apartment):
            message_id = MESSAGES[visitor_chat_id][chat_id]

            if message_id != query.message.message_id:
                context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="Visitante recusado por outro morador!"
                        )

        text = query.message.text
        text = text[31:]
        text = "*RECUSADO*" + text

        context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                parse_mode='Markdown'
                )

        context.bot.send_message(
                chat_id=visitor_chat_id,
                text="Visita recusada!"
                )

        MESSAGES[visitor_chat_id] = {}

    def text(data):
        """Resident notification message text"""
        return f"""
*Visitante requisitando entrada:*

- *Nome:* {data['name']}
- *CPF:* {data['cpf']}
"""

    def buttons():
        """Create the notification buttons"""
        keyboard = [
                [InlineKeyboardButton('Autorizar', callback_data='aut')],
                [InlineKeyboardButton('Recusar', callback_data='ref')],
                ]

        return InlineKeyboardMarkup(keyboard)
