from checks import CheckResident, CheckCondo
from python_speech_features import mfcc
from scipy.io.wavfile import read
import librosa
from settings import LOG_NAME
from settings import NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, VOICE_REGISTER, REPEAT_VOICE
from settings import PATH, CATCH_AUDIO_SPEAKING_NAME, CONFIRM_AUDIO_SPEAKING_NAME
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm
import json
import logging
import numpy
import os
import requests
import subprocess

logger = logging.getLogger(LOG_NAME)

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

        update.message.reply_text('Agora preciso que você grave um áudio dizendo seu nome completo.')
        update.message.reply_text('O áudio deve ter no mínimo 1 segundo e no máximo 3 segundos.')

        return CATCH_AUDIO_SPEAKING_NAME

    def catch_audio_speaking_name(update, context):
        chat_id = update.message.chat_id
        audio = update.message.voice

        logger.debug('\t\tAudio catched.')
        if ValidateForm.audio_speaking_name(audio, update) is False:
            return CATCH_AUDIO_SPEAKING_NAME

        chat[chat_id]['audio_speaking_name'] = audio

        logger.debug('\tRequesting user confirmation ...')
        next_button = KeyboardButton('Prosseguir')
        repeat_button = KeyboardButton('Regravar')
        prompt_buttons = [[repeat_button], [next_button]]
        prompt = ReplyKeyboardMarkup(prompt_buttons, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(
            '''
Escute o audio gravado e verifique se:
1 - A fala foi natural e sem grandes pausas
2 - A fala não sofreu cortes nem no fim nem no começo do áudio
            '''
        )
        update.message.reply_text(
            'Caso o áudio cumpra essas exigências, prossiga. Caso contrário, por favor, regrave.',
            reply_markup=prompt
        )

        return CONFIRM_AUDIO_SPEAKING_NAME

    def confirm_audio_speaking_name(update, context):
        chat_id = update.message.chat_id
        choice = update.message.text

        if choice == 'Regravar':
            update.message.reply_text('Ok. Pode regravar.')
            logger.debug('\t\tUser has requested to record again.')
            logger.debug('\tWaiting for audio ...')
            return CATCH_AUDIO_SPEAKING_NAME

        logger.debug('\t\tUser confirmed the audio')

        audio = chat[chat_id]['audio_speaking_name']

        logger.debug('\tDownloading audio file ...')
        audio_file_path = audio.get_file().download()
        logger.debug('\t\tDone')

        logger.debug('\tConverting audio file into .wav ...')
        wav_audio_file_path = audio_file_path.split('.')[0] + '.wav'
        subprocess.run(['ffmpeg', '-i', audio_file_path, wav_audio_file_path], check=True)
        logger.debug('\t\tDone')

        logger.debug('\tOpening the audio file...')
        data, samplerate = librosa.load(wav_audio_file_path, sr=16000, mono=True)
        logger.debug('\t\tDone')

        logger.debug("\tPutting in the chat's dictionary ...")
        chat[chat_id]['audio_speaking_name'] = data.tolist()
        logger.debug('\t\tDone')

        logger.debug('\tDeleting the audio file ...')
        os.remove(wav_audio_file_path)
        os.remove(audio_file_path)
        logger.debug('\t\tDone')

        logger.debug('TASK accomplished successfully')

        update.message.reply_text('Vamos agora catalogar as características da sua voz!')
        update.message.reply_text(
            'Grave uma breve mensagem de voz dizendo a frase: "Juro que sou eu".'
        )

        logger.info("Requesting voice audio ...")

        return VOICE_REGISTER

    def voice_register(update, context):
        chat_id = update.message.chat_id
        voice_register = update.message.voice

        if not ValidateForm.voice(voice_register, update):
            return VOICE_REGISTER

        update.message.reply_text('Ótimo!')

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

        response = Register.register_resident(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("resident registered in database")
            update.message.reply_text('Morador cadastrado no sistema!')
        else:
            logger.error("Registration failed")
            update.message.reply_text('Falha ao cadastrar no sistema!')

        # logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        chat[chat_id] = {}

        return ConversationHandler.END

    def end(update, context):
        logger.info("Canceling registration")
        chat_id = update.message.chat_id

        update.message.reply_text('Cadastro cancelado!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END


    def register_resident(chat_id):
        logger.info("Registering resident")
        query = """
        mutation createResident(
            $completeName: String!,
            $email: String!,
            $phone: String!,
            $cpf: String!,
            $apartment: String!,
            $block: String!,
            $voiceData: String,
            $audioSpeakingName: String,
            ){
            createResident(
                completeName: $completeName,
                email: $email,
                cpf: $cpf,
                phone: $phone,
                apartment: $apartment,
                block: $block,
                voiceData: $voiceData,
                audioSpeakingName: $audioSpeakingName
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
                'mfccAudioSpeakingName': chat[chat_id]['audio_speaking_name']
                }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response

