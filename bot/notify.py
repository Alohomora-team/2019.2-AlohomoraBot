import logging
from db.schema import get_all_admins_chat_ids, get_resident_chat_id, delete_resident
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from admin import Admin

messages = {}

class NotifyAdmin:
    def send_message(context, data):
        resident_chat_id = get_resident_chat_id(data['cpf'])

        messages[resident_chat_id] = {}

        for chat_id in get_all_admins_chat_ids():

            message = context.bot.send_message(
                    chat_id=chat_id,
                    text=NotifyAdmin.text(data),
                    reply_markup=NotifyAdmin.buttons(),
                    parse_mode='Markdown'
                    )

            messages[resident_chat_id][chat_id] = message.message_id

    def accepted(update, context):
        query = update.callback_query

        cpf = [i for i in query.message.text.split('-')[-3].split() if i.isdigit()][0]

        resident_chat_id = get_resident_chat_id(cpf)

        for chat_id in get_all_admins_chat_ids():

            message_id = messages[resident_chat_id][chat_id]

            if message_id != query.message.message_id:

                context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="Morador aprovado por outro administrador!"
                        )

        text = query.message.text
        text = text[30:]
        text = "*APROVADO*" + text

        context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                parse_mode='Markdown'
                )

        email = query.message.text.split('-')[-4].split()[1]

        response = Admin.activate_resident(email)

        context.bot.send_message(
                chat_id=resident_chat_id,
                text="Cadastro aprovado!"
                )

        messages[resident_chat_id] = {}

    def recused(update, context):
        query = update.callback_query

        cpf = [i for i in query.message.text.split('-')[-3].split() if i.isdigit()][0]

        resident_chat_id = get_resident_chat_id(cpf)

        for chat_id in get_all_admins_chat_ids():

            message_id = messages[resident_chat_id][chat_id]

            if message_id != query.message.message_id:

                context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="Morador recusado por outro administrador!"
                        )

        text = query.message.text
        text = text[30:]
        text = "*RECUSADO*" + text

        context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                parse_mode='Markdown'
                )

        email = query.message.text.split('-')[-4].split()[1]

        response = Admin.delete_resident(email)

        context.bot.send_message(
                chat_id=resident_chat_id,
                text="Cadastro recusado."
                )

        delete_resident(cpf)

        messages[resident_chat_id] = {}

    def text(data):
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
       keyboard = [
               [InlineKeyboardButton('Aprovar', callback_data='acc')],
               [InlineKeyboardButton('Recusar', callback_data='rec')],
               ]

       return InlineKeyboardMarkup(keyboard)
