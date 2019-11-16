"""
Controle resident interactions
"""

import json
import logging
import subprocess
import numpy
import requests

from python_speech_features import mfcc
from scipy.io.wavfile import read
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from settings import CPF_AUTH, VOICE_AUTH
from settings import PATH, LOG_NAME
from validator import ValidateForm
from helpers import format_datetime

LOGGER = logging.getLogger(LOG_NAME)

CHAT = {}

class Auth:
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
        update.message.reply_text("Ok. Mas antes, você precisa se autenticar!")
        update.message.reply_text("Caso deseje interromper o processo digite /cancelar")
        update.message.reply_text("Por favor, informe seu CPF:")

        LOGGER.info("Asking for CPF")

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return CPF_AUTH

    @staticmethod
    def cpf(update, context):
        """
        Validate cpf
        """
        chat_id = update.message.chat_id
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return CPF_AUTH

        cpf = ValidateForm.cpf(cpf, update)

        CHAT[chat_id]['cpf'] = cpf
        LOGGER.debug(f"'auth-cpf': '{CHAT[chat_id]['cpf']}'")

        update.message.reply_text('Grave um áudio de no mínimo 1 segundo dizendo "Juro que sou eu"')
        LOGGER.info("Requesting voice audio")

        return VOICE_AUTH
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
            LOGGER.info("resident has been authenticated")
            update.message.reply_text('Autenticado(a) com sucesso!')

            response = HandleEntryVisitor.get_resident_apartment(chat_id)

            resident = response['data']['resident']
            apartment = resident['apartment']

            CHAT[chat_id]['apartment'] = apartment

            response = HandleEntryVisitor.get_entries_pending(chat_id)

            entries = response['data']['entriesVisitorsPending']

            if entries:
                update.message.reply_text('Você possui entrada(s) pendente(s):')
                LOGGER.info("Showing visitors pending to resident")
            else:
                update.message.reply_text('Você não possui entrada(s) pendente(s)')
                LOGGER.info("Apartment don`t have pending entries")
                return HandleEntryVisitor.end(update, context)

            for entry in entries:

                datetime = format_datetime(entry['date'])

                if entry['pending']:
                    update.message.reply_text(
                        "\nNome: "+entry['visitor']['completeName']+
                        "\nCPF: "+entry['visitor']['cpf']+
                        "\nData: "+datetime+
                        "\n\nCódigo: "+str(entry['id'])
                    )

            remove_keyboard = KeyboardButton('Remover todas')
            cancel_keyboard = KeyboardButton('Cancelar')
            keyboard = [[remove_keyboard], [cancel_keyboard]]

            response = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            update.message.reply_text(
                'Para liberar ou remover alguma entrada, digite o respectivo código'+
                '\nPara remover uma entrada especifica, escreva "Remover + seu respectivo código"'
                , reply_markup=response)

            return HANDLE_VISITORS_PENDING

        LOGGER.error("Authentication failed")
        update.message.reply_text('Falha na autenticação!')


        return HandleEntryVisitor.end(update, context)

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
