import logging
from db.schema import get_all_admins_chat_ids
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

messages = {}

class NotifyAdmin:
    def send_message(context, data):

        for chat_id in get_all_admins_chat_ids():

            message = context.bot.send_message(
                    chat_id=chat_id,
                    text=NotifyAdmin.text(data),
                    reply_markup=NotifyAdmin.buttons()
                    )

            messages[chat_id] = message.message_id

    def accepted(update, context):
        query = update.callback_query

        for chat_id in get_all_admins_chat_ids():

            message_id = messages[chat_id]

            if message_id != query.message.message_id:

                context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="Morador autorizado por outro administrador!"
                        )

        context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="Morador autorizado!"
                )

    def recused(update, context):
        query = update.callback_query

        for chat_id in get_all_admins_chat_ids():

            message_id = messages[chat_id]

            if message_id != query.message.message_id:

                context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="Morador recusado por outro administrador!"
                        )

        context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="Morador recusado!"
                )


    def text(data):
        return f"""
        Morador requisitando cadastro:

        - Nome: {data['name']}
        - Telefone: {data['phone']}
        - Email: {data['email']}
        - CPF: {data['cpf']}
        - Bloco: {data['block']}
        - Apartamento: {data['apartment']}
        """

    def buttons():
       keyboard = [
               [InlineKeyboardButton('Autorizar', callback_data='acc')],
               [InlineKeyboardButton('Recusar', callback_data='rec')],
               ]

       return InlineKeyboardMarkup(keyboard)
