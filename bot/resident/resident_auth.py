"""
Controle resident interactions
"""

import json
import logging
import subprocess
import numpy
import requests

from db.schema import resident_exits, get_resident_cpf
from python_speech_features import mfcc
from scipy.io.wavfile import read
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from checks import CheckResident
from settings import CPF_AUTH, VOICE_AUTH, PASSWORD_AUTH, CHOOSE_AUTH
from settings import SHOW_VISITORS, HANDLE_VISITORS_PENDING
from settings import PATH, LOG_NAME
from validator import ValidateForm
from helpers import format_datetime

LOGGER = logging.getLogger(LOG_NAME)

CHAT = {}

class ResidentAuth:
    """
    Authenticate users
    """

    @staticmethod
    def index(update, context):
        """
        Start interaction
        """
        chat_id = update.message.chat_id

        LOGGER.info("Introducing authentication session")
        update.message.reply_text("")

        if resident_exists(chat_id):
            LOGGER.info("Resident in database - proceed")
            CHAT[chat_id] = {}
            CHAT[chat_id]['cpf'] = get_resident_cpf(chat_id)

        else:
            LOGGER.info("Resident not in database - canceling")
            update.message.reply_text("Você não está registrado. Digite /cadastrar para fazer o cadastro.")
            return ConversationHandler.END

        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        pwd_keyboard = KeyboardButton('Senha')
        voice_keyboard = KeyboardButton('Voz')
        keyboard = [[pwd_keyboard], [voice_keyboard]]
        choice = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('De que maneira deseja se autenticar?', reply_markup=choice)

        return CHOOSE_AUTH

    def choose_auth(update, context):
        """
        Ask for the method to authenticate
        """
        chat_id = update.message.chat_id
        choice = update.message.text

        CHAT[chat_id]['choice'] = choice
        LOGGER.debug(f"'choice': '{CHAT[chat_id]['choice']}'")

        if choice == "Senha":
            LOGGER.info("Replied to authenticate by password")
            update.message.reply_text('Ok! Informe sua senha:')
            LOGGER.info("Requesting password")
            return PASSWORD_AUTH
        elif choice == "Voz":
            LOGGER.info("Replied to authenticate by voice")
            update.message.reply_text(
                'Grave um áudio de no mínimo 1 segundo dizendo "Juro que sou eu"'
            )
            LOGGER.info("Requesting voice audio")
            return VOICE_AUTH
        else:
            update.message.reply_text('Por favor, apenas aperte um dos botões.')
            return CHOOSE_AUTH

    @staticmethod
    def password(update, context):
        """
        Validate password
        """
        chat_id = update.message.chat_id
        password = update.message.text

        CHAT[chat_id]['password'] = password
        LOGGER.debug(f"'password': '{CHAT[chat_id]['password']}'")

        getEmail = Auth.get_email(chat_id)

        if(getEmail.status_code == 200 and 'errors' not in getEmail.json().keys()):
            LOGGER.info("Sucess on getting email by CPF")

            email = getEmail.json()['data']['resident']['email']
            CHAT[chat_id]['email'] = email
            LOGGER.debug(f"'resident-email': '{CHAT[chat_id]['email']}'")

            response = Auth.generate_token(chat_id)
        else:
            LOGGER.error("Failed getting email by CPF")
            update.message.reply_text(
                'Falha ao buscar informações do morador de CPF %s' % CHAT[chat_id]['cpf']
            )

            return ConversationHandler.END

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            LOGGER.info("Sucess on generating token")

            token = response.json()['data']['tokenAuth']['token']
            CHAT[chat_id]['token'] = token
            LOGGER.debug(f"'auth-resident-token': '{CHAT[chat_id]['token']}'")

            return SHOW_VISITORS
        else:
            LOGGER.error("Failed generating token")
            update.message.reply_text(
                'Senha incorreta. Não foi possível autenticar o morador.'
            )
            update.message.reply_text(
                'Se você tem certeza da senha inserida,'+
                ' é possível que sua conta como morador não esteja ativa.'
            )

        return ConversationHandler.END

    @staticmethod
    def voice(update, context):
        """
        Validate voice
        """
        chat_id = update.message.chat_id
        voice_auth = update.message.voice

        if not ValidateForm.voice(voice_auth, update):
            return VOICE_AUTH

        file_auth = voice_auth.get_file()

        src = file_auth.download()
        dest = src.split('.')[0] + ".wav"

        subprocess.run(['ffmpeg', '-i', src, dest])

        samplerate, voice_data = read(dest)

        mfcc_data = mfcc(voice_data, samplerate=samplerate, nfft=1200, winfunc=numpy.hamming)
        mfcc_data = mfcc_data.tolist()
        mfcc_data = json.dumps(mfcc_data)

        CHAT[chat_id]['voice_mfcc'] = mfcc_data
        LOGGER.debug('auth-voice-mfcc:')
        LOGGER.debug(
            f"'{CHAT[chat_id]['voice_mfcc'][:1]}...{CHAT[chat_id]['voice_mfcc'][-1:]}'"
            )

        response = Auth.authenticate(chat_id)

        valid = response['data']['voiceBelongsResident']

        if valid:
            LOGGER.info("Resident has been authenticated")
            update.message.reply_text('Autenticado(a) com sucesso!')

        else:
            LOGGER.error("Authentication failed")
            update.message.reply_text('Falha na autenticação!')

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """

        logger.info("Canceling authentication")
        chat_id = update.message.chat_id

        update.message.reply_text('Autenticação cancelada!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

    def get_email(chat_id):
        """
        Get resident's email by CPF
        """
        LOGGER.info("Getting resident's email by CPF")
        query = """
            query resident($cpf: String!){
                resident(cpf: $cpf){
                    email
                }
            }
        """

        variables = {
                'cpf': CHAT[chat_id]['cpf'],
                }
        response = requests.post(PATH, json={'query':query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response


    def generate_token(chat_id):
        """
        Generate resident's token
        """
        LOGGER.info("Generating resident token")
        query = """
            mutation tokenAuth($email: String!, $password: String!){
                tokenAuth(email: $email, password: $password){
                    token
                }
            }
            """

        variables = {
                'email': CHAT[chat_id]['email'],
                'password': CHAT[chat_id]['password'],
                }
        response = requests.post(PATH, json={'query':query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response

    @staticmethod
    def authenticate(chat_id):
        """
        Authenticate user
        """

        LOGGER.info("Authenticating resident")
        query = """
            query voiceBelongsResident(
                $cpf: String!,
                $mfccData: String
            ){
                voiceBelongsResident(cpf: $cpf, mfccData: $mfccData)
            }
        """

        variables = {
            'cpf': CHAT[chat_id]['cpf'],
            'mfccData': CHAT[chat_id]['voice_mfcc']
        }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        LOGGER.debug(f"Response: {response.json()}")

        return response.json()
