from checks import CheckUser, CheckCondo
from python_speech_features import mfcc
from scipy.io.wavfile import read
from settings import NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, VOICE_REGISTER, REPEAT_VOICE
from settings import PATH
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm
import logging
import json
import numpy
import os
import requests
import subprocess

logger = logging.getLogger('Alohomora')

chat = {}

class Register:

    def index(update, context):
        logger.info("Introducing registration session")
        chat_id = update.message.chat_id

        update.message.reply_text('Ok, vamos iniciar o cadastro!')
        update.message.reply_text('Caso deseje interromper o processo digite /cancelar')
        update.message.reply_text('Nome:')
        logger.info("Asking for name")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return NAME

    def name(update, context):
        chat_id = update.message.chat_id
        name = update.message.text

        if not ValidateForm.name(name, update):
            return NAME

        chat[chat_id]['name'] = name
        logger.debug(f"'name': '{chat[chat_id]['name']}'")

        contact_keyboard = KeyboardButton('Enviar meu número de telefone', request_contact=True)
        custom_keyboard = [[ contact_keyboard ]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keyboard=True)

        update.message.reply_text('Telefone:', reply_markup=reply_markup)
        logger.info("Asking for phone")

        return PHONE

    def phone(update, context):
        chat_id = update.message.chat_id
        phone = update.message.text
        contact = update.effective_message.contact

        if not ValidateForm.phone(phone, contact, update):
            update.message.reply_text('Dado incorreto. Digite novamente:')
            return PHONE

        phone = ValidateForm.phone(phone, contact, update)

        chat[chat_id]['phone'] = phone
        logger.debug(f"'phone': '{chat[chat_id]['phone']}'")

        update.message.reply_text('Email:')
        logger.info("Asking for email")

        return EMAIL

    def email(update, context):
        chat_id = update.message.chat_id
        email = update.message.text

        if not ValidateForm.email(email, update):
            return EMAIL

        chat[chat_id]['email'] = email
        logger.debug(f"'email': '{chat[chat_id]['email']}'")

        check = CheckUser.email(chat, chat_id)

        if 'errors' not in check.keys():
            logger.error("Email already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este email, tente novamente:')
            return EMAIL

        logger.debug("Available email - proceed")

        update.message.reply_text('CPF:')
        logger.info("Asking for CPF")

        return CPF

    def cpf(update, context):
        chat_id = update.message.chat_id
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return CPF

        cpf = ValidateForm.cpf(cpf, update)

        chat[chat_id]['cpf'] = cpf
        logger.debug(f"'cpf': '{chat[chat_id]['cpf']}'")

        check = CheckUser.cpf(chat, chat_id)

        if 'errors' not in check.keys():
            logger.error("CPF already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este CPF, tente novamente:')
            return CPF

        logger.debug("Available CPF - proceed")

        logger.info("Asking for block number")

        update.message.reply_text('Bloco:')

        return BLOCK


    def block(update, context):
        chat_id = update.message.chat_id
        block = update.message.text

        if not ValidateForm.block(block, update):
            return BLOCK

        chat[chat_id]['block'] = block
        logger.debug(f"'block': '{chat[chat_id]['block']}'")

        check = CheckCondo.block(chat, chat_id)

        if 'errors' in check.keys():
            logger.error("Block not found - asking again")
            update.message.reply_text('Por favor, digite um bloco existente:')
            return BLOCK

        logger.debug("Existing block - proceed")

        update.message.reply_text('Apartamento:')
        logger.info("Asking for apartment number")

        return APARTMENT

    def apartment(update, context):
        chat_id = update.message.chat_id
        apartment = update.message.text

        if not ValidateForm.apartment(apartment, update):
            return APARTMENT

        chat[chat_id]['apartment'] = apartment
        logger.debug(f"'apartment': '{chat[chat_id]['apartment']}'")

        check = CheckCondo.apartment(chat, chat_id)

        if 'errors' in check.keys():
            logger.error("Apartment not found - asking again")
            update.message.reply_text('Por favor, digite um apartamento existente:')
            return APARTMENT

        logger.debug("Existing apartment - proceed")

        update.message.reply_text(
            'Vamos agora cadastrar a sua voz! Grave uma breve mensagem de voz dizendo "Juro que sou eu"')

        logger.info("Requesting voice audio")

        return VOICE_REGISTER

    def voice_register(update, context):
        chat_id = update.message.chat_id
        voice_register = update.message.voice

        if not ValidateForm.voice(voice_register, update):
            return VOICE_REGISTER

        f_reg = voice_register.get_file()

        src = f_reg.download()
        dest = src.split('.')[0] + ".wav"

        subprocess.run(['ffmpeg', '-i', src, dest])

        samplerate, voice_data = read(dest)

        mfcc_data = mfcc(voice_data, samplerate=samplerate,
                         nfft=1200, winfunc=numpy.hamming)
        mfcc_data = mfcc_data.tolist()
        mfcc_data = json.dumps(mfcc_data)

        chat[chat_id]['voice_reg'] = None
        chat[chat_id]['voice_mfcc'] = mfcc_data
        logger.debug(f"'voice_reg': '{chat[chat_id]['voice_reg']}'")
        logger.debug(f"'voice_mfcc': '{chat[chat_id]['voice_mfcc'][:1]}...{chat[chat_id]['voice_mfcc'][-1:]}'")

        # Repeat and confirm buttons
        repeat_keyboard = KeyboardButton('Repetir')
        confirm_keyboard = KeyboardButton('Confirmar')
        keyboard = [[repeat_keyboard],[confirm_keyboard]]
        choice = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Escute o seu áudio e confirme se está com boa qualidade', reply_markup = choice)

        logger.info("Asking to confirm or repeat voice audio")

        return REPEAT_VOICE

    def repeat_voice(update, context):
        chat_id = update.message.chat_id
        choice = update.message.text

        if choice == "Repetir":
            logger.debug("Repeating voice audio")
            update.message.reply_text('Por favor, grave novamente:')
            return VOICE_REGISTER

        logger.debug("Confirming voice audio")

        response = Register.register_user(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("User registered in database")
            update.message.reply_text('Morador cadastrado no sistema!')
        else:
            logger.error("Registration failed")
            update.message.reply_text('Falha ao cadastrar no sistema!')

        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        chat[chat_id] = {}

        return ConversationHandler.END

    def end(update, context):
        logger.info("Canceling registration")
        chat_id = update.message.chat_id

        update.message.reply_text('Cadastro cancelado!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END


    def register_user(chat_id):
        logger.info("Registering user")
        query = """
        mutation createResident(
            $completeName: String!,
            $email: String!,
            $phone: String!,
            $cpf: String!,
            $apartment: String!,
            $block: String!,
            $voiceData: String,
            $mfccData: String,
            ){
            createResident(
                completeName: $completeName,
                email: $email,
                cpf: $cpf,
                phone: $phone,
                apartment: $apartment,
                block: $block,
                voiceData: $voiceData
                mfccData: $mfccData
            ){
                resident{
                    completeName
                    email
                    cpf
                    phone
                    apartment{
                        number
                        block{
                            number
                        }
                    }
                }
            }
        }
        """

        variables = {
                'completeName': chat[chat_id]['name'],
                'email': chat[chat_id]['email'],
                'phone': chat[chat_id]['phone'],
                'cpf': chat[chat_id]['cpf'],
                'apartment': chat[chat_id]['apartment'],
                'block': chat[chat_id]['block'],
                'voiceData': chat[chat_id]['voice_reg'],
                'mfccData': chat[chat_id]['voice_mfcc']
                }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response
