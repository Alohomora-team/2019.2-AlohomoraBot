"""
Register a user interaction
"""
import json
import logging
import os
import subprocess
import numpy
import requests
import librosa

from checks import CheckResident, CheckCondo
from db.schema import create_resident, resident_exists
from admin.notify_admin import NotifyAdmin
from settings import LOG_NAME
from settings import NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, PASSWORD
from settings import VOICE_REGISTER, REPEAT_VOICE
from settings import PATH, CATCH_AUDIO_SPEAKING_NAME, CONFIRM_AUDIO_SPEAKING_NAME
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm


logger = logging.getLogger(LOG_NAME)

chat = {}

class RegisterResident:
    """
    Register a resident
    """

    def index(update, context):
        """
        Start the conversation
        """
        logger.info("Introducing registration session")
        chat_id = update.message.chat_id

        if resident_exists(chat_id):
            update.message.reply_text('Você já está cadastrado!')
            return ConversationHandler.END

        update.message.reply_text('Ok, vamos iniciar o cadastro!')
        update.message.reply_text('Caso deseje interromper o processo digite /cancelar')
        update.message.reply_text('Nome:')
        logger.info("Asking for name")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return NAME

    def name(update, context):
        """
        Get name of a resident
        """
        chat_id = update.message.chat_id
        name = update.message.text

        if not ValidateForm.name(name, update):
            return NAME

        chat[chat_id]['name'] = name
        logger.debug(f"'name': '{chat[chat_id]['name']}'")

        contact_keyboard = KeyboardButton('Enviar meu número de telefone', request_contact=True)
        custom_keyboard = [[contact_keyboard]]
        reply_markup = ReplyKeyboardMarkup(
            custom_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )

        update.message.reply_text('Telefone:', reply_markup=reply_markup)
        logger.info("Asking for phone")

        return PHONE

    def phone(update, context):
        """
        Get phone information
        """
        chat_id = update.message.chat_id
        phone = update.message.text
        contact = update.effective_message.contact

        if not ValidateForm.phone(phone, contact, update):
            return PHONE

        phone = ValidateForm.phone(phone, contact, update)

        chat[chat_id]['phone'] = phone
        logger.debug(f"'phone': '{chat[chat_id]['phone']}'")

        update.message.reply_text('Email:')
        logger.info("Asking for email")

        return EMAIL

    def email(update, context):
        """
        Get email information
        """

        chat_id = update.message.chat_id
        email = update.message.text

        if not ValidateForm.email(email, update):
            return EMAIL

        chat[chat_id]['email'] = email
        logger.debug(f"'email': '{chat[chat_id]['email']}'")

        check = CheckResident.email(chat, chat_id)

        if 'errors' not in check.keys():
            logger.error("Email already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este email, tente novamente:')
            return EMAIL

        logger.debug("Available email - proceed")

        update.message.reply_text('CPF:')
        logger.info("Asking for CPF")

        return CPF

    def cpf(update, context):
        """
        Get cpf information
        """

        chat_id = update.message.chat_id
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return CPF

        cpf = ValidateForm.cpf(cpf, update)

        chat[chat_id]['cpf'] = cpf
        logger.debug(f"'cpf': '{chat[chat_id]['cpf']}'")

        check = CheckResident.cpf(chat, chat_id)

        if 'errors' not in check.keys():
            logger.error("CPF already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este CPF, tente novamente:')
            return CPF

        logger.debug("Available CPF - proceed")

        logger.info("Asking for block number")

        update.message.reply_text('Bloco:')

        return BLOCK


    def block(update, context):
        """
        Get block information
        """

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
        """
        Get apartment information
        """

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
            'Grave uma breve mensagem de voz dizendo a frase: "Juro que sou eu".'
        )

        return VOICE_REGISTER

    def voice_register(update, context):
        """
        Catch the phrase audio and ask for confirmation
        """
        chat_id = update.message.chat_id
        audio = update.message.voice

        if not ValidateForm.voice(audio, update):
            return VOICE_REGISTER

        chat[chat_id]['audio_speaking_phrase'] = audio

        # Repeat and confirm buttons
        repeat_keyboard = KeyboardButton('Repetir')
        confirm_keyboard = KeyboardButton('Confirmar')
        keyboard = [[repeat_keyboard], [confirm_keyboard]]
        choice = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(
            'Escute o seu áudio e confirme se está com boa qualidade',
            reply_markup=choice
        )

        logger.info("Asking to confirm or repeat voice audio ...")

        return REPEAT_VOICE

    def repeat_voice(update, context):
        """
        Repeate voice interaction
        """

        chat_id = update.message.chat_id
        choice = update.message.text

        if choice == "Repetir":
            logger.debug("Repeating voice audio ...")
            update.message.reply_text('Por favor, grave novamente:')
            return VOICE_REGISTER

        logger.debug("\tAudio confirmed")

        logger.debug('Downloading audio ...')
        audio_file_path = chat[chat_id]['audio_speaking_phrase'].get_file().download()
        wav_audio_file_path = audio_file_path.split('.')[0] + '.wav'
        logger.debug('\tDone')

        logger.debug('Converting into wav ...')
        subprocess.run(['ffmpeg', '-i', audio_file_path, wav_audio_file_path], check=True)
        logger.debug('\tDone')

        logger.debug('Opening audio and resampling ...')
        data, samplerate = librosa.load(wav_audio_file_path, sr=16000, mono=True)
        logger.debug('\tDone')

        logger.debug('Putting into dictionary ...')
        chat[chat_id]['audio_speaking_phrase'] = data.tolist()
        logger.debug('\tDone')

        logger.debug('Removindo audio files ...')
        os.remove(audio_file_path)
        os.remove(wav_audio_file_path)
        logger.debug('\tDone')

        update.message.reply_text(
            'Além da autenticação de moradores por voz, é possível fazê-la por senha.'
        )
        update.message.reply_text('Por favor, informe a senha que deseja cadastrar:')
        logger.info("Asking for password")

        return PASSWORD

    def password(update, context):
        """
        Request password
        """

        chat_id = update.message.chat_id
        password = update.message.text

        chat[chat_id]['password'] = password
        logger.debug(f"'password': '{chat[chat_id]['password']}'")

        response = Register.register_resident(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Resident registered in database")
            update.message.reply_text("Cadastro feito!\nAguarde aprovação dos administradores.")

            create_resident(
                    cpf=chat[chat_id]['cpf'],
                    block=chat[chat_id]['block'],
                    apartment=chat[chat_id]['apartment'],
                    chat_id=chat_id
                    )
            NotifyAdmin.send_message(context, chat[chat_id])
        else:
            logger.error("Registration failed")
            update.message.reply_text('Falha ao cadastrar no sistema!')

        chat[chat_id] = {}

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """

        logger.info("Canceling registration")
        chat_id = update.message.chat_id

        update.message.reply_text('Cadastro cancelado!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

    def register_resident(chat_id):
        """
        Register a resident
        """

        logger.info("Registering resident")
        query = """
        mutation createResident(
            $completeName: String!,
            $email: String!,
            $phone: String!,
            $cpf: String!,
            $apartment: String!,
            $block: String!,
            $audioSpeakingPhrase: [Float]!
            $audioSpeakingName: [Float]!,
            $audioSamplerate: Int,
            $password: String!
            ){
            createResident(
                completeName: $completeName,
                email: $email,
                cpf: $cpf,
                phone: $phone,
                apartment: $apartment,
                block: $block,
                audioSpeakingPhrase: $audioSpeakingPhrase,
                audioSpeakingName: $audioSpeakingName,
                password: $password
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
                    password
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
                'audioSpeakingPhrase': chat[chat_id]['audio_speaking_phrase'],
                'audioSpeakingName': "Nada",
                'password': chat[chat_id]['password'],
                }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response
