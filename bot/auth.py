from python_speech_features import mfcc
from scipy.io.wavfile import read
from settings import CPF_AUTH, VOICE_AUTH
from settings import PATH, LOG_NAME
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

class Auth:

    def index(update, context):
        chat_id = update.message.chat_id

        logger.info("Introducing authentication session")
        update.message.reply_text("Ok, vamos te autenticar!")
        update.message.reply_text("Caso deseje interromper o processo digite /cancelar")
        update.message.reply_text("Por favor, informe seu CPF:")

        logger.info("Asking for CPF")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return CPF_AUTH

    def cpf(update, context):
        chat_id = update.message.chat_id
        cpf = update.message.text

        if not ValidateForm.cpf(cpf, update):
            return CPF_AUTH

        cpf = ValidateForm.cpf(cpf, update)

        chat[chat_id]['cpf'] = cpf
        logger.debug(f"'auth-cpf': '{chat[chat_id]['cpf']}'")

        update.message.reply_text('Grave um áudio de no mínimo 1 segundo dizendo "Juro que sou eu"')
        logger.info("Requesting voice audio")

        return VOICE_AUTH

    def voice(update, context):
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

        chat[chat_id]['voice_mfcc'] = mfcc_data
        logger.debug(f"'auth-voice-mfcc': '{chat[chat_id]['voice_mfcc'][:1]}...{chat[chat_id]['voice_mfcc'][-1:]}'")

        response = Auth.authenticate(chat_id)

        valid = response['data']['voiceBelongsResident']

        if valid:
            logger.info("User has been authenticated")
            update.message.reply_text('Autenticado(a) com sucesso!')
        else:
            logger.error("Authentication failed")
            update.message.reply_text('Falha na autenticação!')

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

    def end(update, context):
        chat_id = update.message.chat_id
        update.message.reply_text('Autenticação cancelada!')
        logger.info("Canceling authentication")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

    def authenticate(chat_id):
        logger.info("Authenticating user")
        query = """
        query voiceBelongsResident(
            $cpf: String!,
            $mfccData: String
        ){
            voiceBelongsResident(cpf: $cpf, mfccData: $mfccData)
        }
        """

        variables = {
                'cpf': chat[chat_id]['cpf'],
                'mfccData': chat[chat_id]['voice_mfcc']
        }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response.json()
