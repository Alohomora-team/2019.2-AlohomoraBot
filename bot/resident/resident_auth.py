"""
Controle resident interactions
"""

import json
import logging
import subprocess
import numpy
import requests

from checks import CheckResident
from db.schema import resident_exists, get_resident_cpf, update_resident
from helpers import format_datetime
from python_speech_features import mfcc
from scipy.io.wavfile import read
from settings import CHOOSE_AUTH, VOICE_AUTH, PASSWORD_AUTH
from settings import PATH, LOG_NAME, API_TOKEN
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from validator import ValidateForm

logger = logging.getLogger(LOG_NAME)

class ResidentAuth:
    """
    Authenticate users
    """
    @staticmethod
    def index(update, context):
        """
        Start interaction
        """

        logger.info("Introducing authentication session")
        update = update.callback_query
        chat_id = update.message.chat_id

        if resident_exists(chat_id):
            logger.info("Resident in database - proceed")
            context.chat_data['cpf'] = get_resident_cpf(chat_id)

            context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=update.message.message_id,
                    text="""
Digite /cancelar caso queira interromper o processo.
                    """
                    )
        else:
            logger.info("Resident not in database - canceling")
            update.message.reply_text("Você precisa estar registrado para se autenticar.")

            context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=update.message.message_id,
                    )
            return ConversationHandler.END

        logger.debug(f"data: {context.chat_data}")

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
        choice = update.message.text

        context.chat_data['choice'] = choice
        logger.debug(f"'choice': '{context.chat_data['choice']}'")

        if choice == "Senha":
            logger.info("Replied to authenticate by password")
            update.message.reply_text('Informe sua senha:')
            logger.info("Requesting password")
            return PASSWORD_AUTH
        elif choice == "Voz":
            logger.info("Replied to authenticate by voice")
            update.message.reply_text(
                'Grave um áudio de no mínimo 1 segundo dizendo "Juro que sou eu"'
            )
            logger.info("Requesting voice audio")
            return VOICE_AUTH
        else:
            update.message.reply_text('Por favor, apenas aperte um dos botões.')
            return CHOOSE_AUTH

    @staticmethod
    def password(update, context):
        """
        Validate password
        """
        password = update.message.text

        context.chat_data['password'] = password
        logger.debug(f"'password': '{context.chat_data['password']}'")

        getEmail = ResidentAuth.get_email(context.chat_data['cpf'])

        if(getEmail.status_code == 200 and 'errors' not in getEmail.json().keys()):
            logger.info("Sucess on getting email by CPF")
            email = getEmail.json()['data']['resident']['email']
            context.chat_data['email'] = email
            logger.debug(f"'email': '{context.chat_data['email']}'")
        else:
            logger.error("Failed getting email by CPF")
            update.message.reply_text(
                'Falha ao buscar informações do morador de CPF %s' % context.chat_data['cpf']
            )

            return ConversationHandler.END

        response = ResidentAuth.generate_token(context.chat_data)

        if(response.status_code == 200 and 'errors' not in response.json().keys()):
            logger.info("Sucess on generating token")
            token = response.json()['data']['tokenAuth']['token']
            logger.debug(f"'token': '{token}'")

            update.message.reply_text('Autenticado(a) com sucesso!')

            update_resident(cpf=context.chat_data['cpf'], token=token)
        else:
            logger.error("Failed generating token")
            update.message.reply_text(
                'Senha incorreta ou você ainda não foi autorizado pelos administradores.'
            )

        logger.debug(f"data: {context.chat_data}")
        context.chat_data.clear()

        return ConversationHandler.END

    @staticmethod
    def voice(update, context):
        """
        Validate voice
        """
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

        context.chat_data['audioSpeakingPhrase'] = mfcc_data

        response = ResidentAuth.authenticate(context.chat_data)

        valid = response['data']['voiceBelongsResident']

        if valid:
            logger.info("Resident has been authenticated")
            update.message.reply_text('Autenticado(a) com sucesso!')
        else:
            logger.error("Authentication failed")
            update.message.reply_text('Falha na autenticação!')

        logger.debug(f"data: {context.chat_data}")
        context.chat_data.clear()

        return ConversationHandler.END

    def end(update, context):
        """
        Cancel interaction
        """

        logger.info("Canceling authentication")

        update.message.reply_text('Autenticação cancelada!')

        logger.debug(f"data: {context.chat_data}")
        context.chat_data.clear()

        return ConversationHandler.END

    def get_email(cpf):
        """
        Get resident's email by CPF
        """
        logger.info("Getting resident's email by CPF")
        query = """
            query resident($cpf: String!){
                resident(cpf: $cpf){
                    email
                }
            }
        """

        variables = {
                'cpf': cpf,
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(PATH, headers=headers, json={'query':query, 'variables':variables})
        logger.debug(f"Response: {response.json()}")

        return response


    def generate_token(data):
        """
        Generate resident's token
        """
        logger.info("Generating resident token")
        query = """
            mutation tokenAuth($email: String!, $password: String!){
                tokenAuth(email: $email, password: $password){
                    token
                }
            }
            """

        variables = {
                'email': data['email'],
                'password': data['password'],
                }

        response = requests.post(PATH, json={'query':query, 'variables':variables})
        logger.debug(f"Response: {response.json()}")

        return response

    @staticmethod
    def authenticate(data):
        """
        Authenticate user
        """
        logger.info("Authenticating resident")
        query = """
            query voiceBelongsResident(
                $cpf: String!,
                $audioSpeakingPhrase: [Float]!,
            ){
                voiceBelongsResident(
                cpf: $cpf,
                audioSpeakingPhrase: $audioSpeakingPhrase)
            }
        """

        variables = {
            'cpf': data['cpf'],
            'audioSpeakingPhrase': data['audioSpeakingPhrase']
        }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(PATH, headers=headers, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response.json()
