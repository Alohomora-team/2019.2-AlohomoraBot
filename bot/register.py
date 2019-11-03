import json
import logging
import subprocess
import numpy
import requests
from python_speech_features import mfcc
from scipy.io.wavfile import read
from checks import CheckResident, CheckCondo
from settings import LOG_NAME
from settings import NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, VOICE_REGISTER, REPEAT_VOICE
from settings import PATH
from settings import CATCH_AUDIO_SPEAKING_NAME, CONFIRM_AUDIO_SPEAKING_NAME
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm

LOGGER = logging.getLogger(LOG_NAME)

CHAT = {}

class Register:

    @staticmethod
    def index(update, context):
        LOGGER.info("Introducing registration session")
        chat_id = update.message.chat_id

        update.message.reply_text('Ok, vamos iniciar o cadastro!')
        update.message.reply_text('Caso deseje interromper o processo digite /cancelar')
        update.message.reply_text('Nome:')
        LOGGER.info("Asking for name")

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return NAME

    @staticmethod
    def name(update, context):
        chat_id = update.message.chat_id
        name = update.message.text

        if not ValidateForm.name(name, update):
            return NAME

        CHAT[chat_id]['name'] = name
        LOGGER.debug(f"'name': '{CHAT[chat_id]['name']}'")

        contact_keyboard = KeyboardButton('Enviar meu número de telefone', request_contact=True)
        custom_keyboard = [[contact_keyboard]]
        reply_markup = ReplyKeyboardMarkup(
            custom_keyboard, one_time_keyboard=True, resize_keyboard=True
        )

        update.message.reply_text('Telefone:', reply_markup=reply_markup)
        LOGGER.info("Asking for phone")

        return PHONE

    @staticmethod
    def phone(update, context):
        chat_id = update.message.chat_id
        phone = update.message.text
        contact = update.effective_message.contact

        if not ValidateForm.phone(phone, contact, update):
            return PHONE

        phone = ValidateForm.phone(phone, contact, update)

        CHAT[chat_id]['phone'] = phone
        LOGGER.debug(f"'phone': '{CHAT[chat_id]['phone']}'")

        update.message.reply_text('Email:')
        LOGGER.info("Asking for email")

        return EMAIL

    @staticmethod
    def email(update, context):
        chat_id = update.message.chat_id
        email = update.message.text

        if not ValidateForm.email(email, update):
            return EMAIL

        CHAT[chat_id]['email'] = email
        LOGGER.debug(f"'email': '{CHAT[chat_id]['email']}'")

        check = CheckResident.emai chat_id)

        if 'errors' not in check.keys():
            LOGGER.error("Email already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este email, tente novamente:')
            return EMAIL

        LOGGER.debug("Available email - proceed")

        update.message.reply_text('CPF:')
        LOGGER.info("Asking for CPF")

        return CPF

    @staticmethod
    def cpf(update, context):
        chat_id = update.message.chat_id
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return CPF

        cpf = ValidateForm.cpf(cpf, update)

        CHAT[chat_id]['cpf'] = cpf
        LOGGER.debug(f"'cpf': '{CHAT[chat_id]['cpf']}'")

        check = CheckResident.cp chat_id)

        if 'errors' not in check.keys():
            LOGGER.error("CPF already exists in database - asking again")
            update.message.reply_text('Já existe um morador com este CPF, tente novamente:')
            return CPF

        LOGGER.debug("Available CPF - proceed")

        LOGGER.info("Asking for block number")

        update.message.reply_text('Bloco:')

        return BLOCK

    @staticmethod
    def block(update, context):
        chat_id = update.message.chat_id
        block = update.message.text

        if not ValidateForm.block(block, update):
            return BLOCK

        CHAT[chat_id]['block'] = block
        LOGGER.debug(f"'block': '{CHAT[chat_id]['block']}'")

        check = CheckCondo.bloc chat_id)

        if 'errors' in check.keys():
            LOGGER.error("Block not found - asking again")
            update.message.reply_text('Por favor, digite um bloco existente:')
            return BLOCK

        LOGGER.debug("Existing block - proceed")

        update.message.reply_text('Apartamento:')
        LOGGER.info("Asking for apartment number")

        return APARTMENT

    @staticmethod
    def apartment(update, context):
        chat_id = update.message.chat_id
        apartment = update.message.text

        if not ValidateForm.apartment(apartment, update):
            return APARTMENT

        CHAT[chat_id]['apartment'] = apartment
        LOGGER.debug(f"'apartment': '{CHAT[chat_id]['apartment']}'")

        check = CheckCondo.apartmen chat_id)

        if 'errors' in check.keys():
            LOGGER.error("Apartment not found - asking again")
            update.message.reply_text('Por favor, digite um apartamento existente:')
            return APARTMENT

        LOGGER.debug("Existing apartment - proceed")
        LOGGER.debug('TASK: Catch audio speaking name')
        LOGGER.debug('\tWaiting for audio ...')

        update.message.reply_text(
            'Agora preciso que você grave um áudio dizendo seu nome completo.'
        )
        update.message.reply_text(
            'O áudio deve ter no mínimo 1 segundo e no máximo 3 segundos.'
        )

        return CATCH_AUDIO_SPEAKING_NAME

    @staticmethod
    def catch_audio_speaking_name(update, context):
        chat_id = update.message.chat_id
        audio = update.message.voice

        LOGGER.debug('\t\tAudio catched.')
        if ValidateForm.audio_speaking_name(audio, update) is False:
            return CATCH_AUDIO_SPEAKING_NAME

        CHAT[chat_id]['mfcc_audio_speaking_name'] = audio

        LOGGER.debug('\tRequesting user confirmation ...')
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

    @staticmethod
    def confirm_audio_speaking_name(update, context):
        chat_id = update.message.chat_id
        choice = update.message.text

        if choice == 'Regravar':
            update.message.reply_text('Ok. Pode regravar.')
            LOGGER.debug('\t\tUser has requested to record again.')
            LOGGER.debug('\tWaiting for audio ...')
            return CATCH_AUDIO_SPEAKING_NAME

        LOGGER.debug('\t\tUser confirmed the audio')

        audio = CHAT[chat_id]['mfcc_audio_speaking_name']

        LOGGER.debug('\tDownloading audio file ...')
        audio_file_path = audio.get_file().download()
        LOGGER.debug('\t\tDone')

        LOGGER.debug('\tConverting audio file into .wav ...')
        wav_audio_file_path = audio_file_path.split('.')[0] + '.wav'
        subprocess.run(['ffmpeg', '-i', audio_file_path, wav_audio_file_path], check=True)
        LOGGER.debug('\t\tDone')

        LOGGER.debug('\tOpening the audio file...')
        samplerate, data = read(wav_audio_file_path)
        LOGGER.debug('\t\tDone')

        LOGGER.debug('\tExtracting MFCC features from audio file ...')
        mfcc_audio_speaking_name = mfcc(
            data,
            samplerate=samplerate,
            nfft=1200,
            winfunc=numpy.hamming
        )
        LOGGER.debug('\t\tDone')

        LOGGER.debug("\tTurning into JSON and putting in the chat's dictionary ...")
        mfcc_audio_speaking_name = json.dumps(mfcc_audio_speaking_name.tolist())
        CHAT[chat_id]['mfcc_audio_speaking_name'] = mfcc_audio_speaking_name
        LOGGER.debug('\t\tDone')

        LOGGER.debug('\tDeleting remaing files ...')
        subprocess.run(['rm', audio_file_path, wav_audio_file_path], check=True)
        LOGGER.debug('\t\tDone')
        LOGGER.debug('TASK accomplished successfully')

        update.message.reply_text('Vamos agora catalogar as características da sua voz!')
        update.message.reply_text(
            'Grave uma breve mensagem de voz dizendo a frase: "Juro que sou eu".'
        )

        LOGGER.info("Requesting voice audio ...")

        return VOICE_REGISTER

    @staticmethod
    def voice_register(update, context):
        chat_id = update.message.chat_id
        voice_register = update.message.voice

        if not ValidateForm.voice(voice_register, update):
            return VOICE_REGISTER

        update.message.reply_text('Ótimo!')

        f_reg = voice_register.get_file()

        src = f_reg.download()
        dest = src.split('.')[0] + ".wav"

        subprocess.run(['ffmpeg', '-i', src, dest], check=True)

        samplerate, voice_data = read(dest)

        mfcc_data = mfcc(voice_data, samplerate=samplerate,
                         nfft=1200, winfunc=numpy.hamming)
        mfcc_data = mfcc_data.tolist()
        mfcc_data = json.dumps(mfcc_data)

        CHAT[chat_id]['voice_reg'] = None
        CHAT[chat_id]['voice_mfcc'] = mfcc_data
        LOGGER.debug(f"'voice_reg': '{CHAT[chat_id]['voice_reg']}'")
        LOGGER.debug(
            f"'voice_mfcc':'{CHAT[chat_id]['voice_mfcc'][:1]}...{CHAT[chat_id]['voice_mfcc'][-1:]}'"
        )

        # Repeat and confirm buttons
        repeat_keyboard = KeyboardButton('Repetir')
        confirm_keyboard = KeyboardButton('Confirmar')
        keyboard = [[repeat_keyboard], [confirm_keyboard]]
        choice = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(
            'Escute o seu áudio e confirme se está com boa qualidade', reply_markup=choice
        )

        LOGGER.info("Asking to confirm or repeat voice audio")

        return REPEAT_VOICE

    @staticmethod
    def repeat_voice(update, context):
        chat_id = update.message.chat_id
        choice = update.message.text

        if choice == "Repetir":
            LOGGER.debug("Repeating voice audio")
            update.message.reply_text('Por favor, grave novamente:')
            return VOICE_REGISTER

        LOGGER.debug("Confirming voice audio")

        response = Register.register_resident(chat_id)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            LOGGER.info("resident registered in database")
            update.message.reply_text('Morador cadastrado no sistema!')
        else:
            LOGGER.error("Registration failed")
            update.message.reply_text('Falha ao cadastrar no sistema!')

        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        CHAT[chat_id] = {}

        return ConversationHandler.END

    @staticmethod
    def end(update, context):
        LOGGER.info("Canceling registration")
        chat_id = update.message.chat_id

        update.message.reply_text('Cadastro cancelado!')

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return ConversationHandler.END

    @staticmethod
    def register_resident(chat_id):
        LOGGER.info("Registering resident")
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
            $mfccAudioSpeakingName: String,
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
                mfccAudioSpeakingName: $mfccAudioSpeakingName
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
            'completeName': CHAT[chat_id]['name'],
            'email': CHAT[chat_id]['email'],
            'phone': CHAT[chat_id]['phone'],
            'cpf': CHAT[chat_id]['cpf'],
            'apartment': CHAT[chat_id]['apartment'],
            'block': CHAT[chat_id]['block'],
            'voiceData': CHAT[chat_id]['voice_reg'],
            'mfccData': CHAT[chat_id]['voice_mfcc'],
            'mfccAudioSpeakingName': CHAT[chat_id]['mfcc_audio_speaking_name']
        }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        LOGGER.debug(f"Response: {response.json()}")

        return response
