"""
Register a user interaction
"""

import json
import logging
import subprocess
import os
import librosa
import numpy
import requests

from admin.notify_admin import NotifyAdmin
from admin.admin import Admin
from checks import CheckResident, CheckCondo
from db.schema import create_resident, resident_exists
from settings import NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, PASSWORD
from settings import VOICE_REGISTER, REPEAT_VOICE
from settings import LOG_NAME, PATH, API_TOKEN
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm
from resident.resident_auth import ResidentAuth

logger = logging.getLogger(LOG_NAME)

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
            logger.info("Resident already registered")
            update.message.reply_text('Você já está cadastrado!')
            return ConversationHandler.END

        update.message.reply_text('Nome:')
        logger.info("Asking for name")

        logger.debug(f"data: {context.chat_data}")

        return NAME

    def name(update, context):
        """
        Get name of a resident
        """
        name = update.message.text

        if not ValidateForm.name(name, update):
            return NAME

        context.chat_data['name'] = name
        logger.debug(f"'name': '{context.chat_data['name']}'")

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
        phone = update.message.text
        contact = update.effective_message.contact

        if not ValidateForm.phone(phone, contact, update):
            return PHONE

        phone = ValidateForm.phone(phone, contact, update)

        context.chat_data['phone'] = phone
        logger.debug(f"'phone': '{context.chat_data['phone']}'")

        update.message.reply_text('Email:')
        logger.info("Asking for email")

        return EMAIL

    def email(update, context):
        """
        Get email information
        """
        email = update.message.text

        if not ValidateForm.email(email, update):
            return EMAIL

        context.chat_data['email'] = email
        logger.debug(f"'email': '{context.chat_data['email']}'")

        check = CheckResident.email(email)

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
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return CPF

        cpf = ValidateForm.cpf(cpf, update)

        context.chat_data['cpf'] = cpf
        logger.debug(f"'cpf': '{context.chat_data['cpf']}'")

        check = CheckResident.cpf(cpf)

        if 'errors' not in check.keys():
            logger.error("CPF already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este CPF, tente novamente:')
            return CPF

        logger.debug("Available CPF - proceed")

        update.message.reply_text('Bloco:')
        logger.info("Asking for block number")

        return BLOCK

    def block(update, context):
        """
        Get block information
        """
        block = update.message.text

        if not ValidateForm.block(block, update):
            return BLOCK

        context.chat_data['block'] = block
        logger.debug(f"'block': '{context.chat_data['block']}'")

        check = CheckCondo.block(block)

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
        apartment = update.message.text
        block = context.chat_data['block']

        if not ValidateForm.apartment(apartment, update):
            return APARTMENT

        context.chat_data['apartment'] = apartment
        logger.debug(f"'apartment': '{context.chat_data['apartment']}'")

        check = CheckCondo.apartment(block, apartment)

        if 'errors' in check.keys():
            logger.error("Apartment not found - asking again")
            update.message.reply_text('Por favor, digite um apartamento existente:')
            return APARTMENT

        logger.debug("Existing apartment - proceed")

        update.message.reply_text(
            'Legal, agora grave um áudio dizendo "Vou trancar o curso".'
        )
        update.message.reply_text(
            'Quando começar a gravar, espere meio segundinho antes de começar a falar, ok?'
        )

        return VOICE_REGISTER

    def voice_register(update, context):
        """
        Catch the phrase audio and ask for confirmation
        """
        audio = update.message.voice

        if not ValidateForm.audio_has_valid_duration(audio, update):
            return VOICE_REGISTER

        context.chat_data['audio_speaking_phrase'] = audio

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
        choice = update.message.text

        if choice == "Repetir":
            logger.debug("Repeating voice audio ...")
            update.message.reply_text('Por favor, grave novamente:')
            return VOICE_REGISTER

        update.message.reply_text('Certo, vou dar uma conferida no áudio')
        logger.debug("\tAudio confirmed")

        logger.debug('Downloading audio ...')
        audio_file_path = context.chat_data['audio_speaking_phrase'].get_file().download()
        wav_audio_file_path = audio_file_path.split('.')[0] + '.wav'
        logger.debug('\tDone')

        logger.debug('Converting into wav ...')
        subprocess.run(['ffmpeg', '-i', audio_file_path, wav_audio_file_path], check=True)
        logger.debug('\tDone')

        logger.debug('Opening audio and resampling ...')
        data, samplerate = librosa.load(wav_audio_file_path, sr=16000, mono=True)
        logger.debug('\tDone')

        logger.debug('Putting into dictionary ...')
        context.chat_data['audio_speaking_phrase'] = data.tolist()
        logger.debug('\tDone')

        logger.debug('Removindo audio files ...')
        os.remove(audio_file_path)
        os.remove(wav_audio_file_path)
        logger.debug('\tDone')

        if not ValidateForm.audio_has_good_volume(data.tolist(), update):
            return VOICE_REGISTER

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

        context.chat_data['password'] = password
        logger.debug(f"'password': '{context.chat_data['password']}'")

        response = RegisterResident.register_resident(context.chat_data)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Resident registered in database")
            update.message.reply_text("Cadastro feito!\nAguarde aprovação dos administradores.")

            Admin.activate_resident(context.chat_data['email'])
            token = ResidentAuth.generate_token(context.chat_data)
            token = token.json()['data']['tokenAuth']['token']
            Admin.deactivate_resident(context.chat_data['email'])

            create_resident(
                    cpf=context.chat_data['cpf'],
                    block=context.chat_data['block'],
                    apartment=context.chat_data['apartment'],
                    chat_id=chat_id,
                    token=token
                    )
            NotifyAdmin.send_message(context, context.chat_data)
        else:
            logger.error("Registration failed")
            update.message.reply_text('Falha ao cadastrar no sistema!')

        logger.debug(f"data: {context.chat_data}")
        context.chat_data.clear()

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """
        logger.info("Canceling registration")

        update.message.reply_text('Cadastro cancelado!')

        logger.debug(f"data: {context.chat_data}")
        context.chat_data.clear()

        return ConversationHandler.END

    def register_resident(data):
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
                }
            }
        }
        """

        variables = {
                'completeName': data['name'],
                'email': data['email'],
                'phone': data['phone'],
                'cpf': data['cpf'],
                'apartment': data['apartment'],
                'block': data['block'],
                'audioSpeakingPhrase': data['audio_speaking_phrase'],
                'audioSpeakingName': data['audio_speaking_phrase'],
                'password': data['password'],
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(PATH, headers=headers, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response
