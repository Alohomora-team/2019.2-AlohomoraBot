from telegram.ext import ConversationHandler
from python_speech_features import mfcc
from scipy.io.wavfile import read
import json
import numpy
import requests
import subprocess
import os

from validator import ValidateForm

CPF_AUTH, VOICE_AUTH = range(2)


PATH = "http://localhost:8000/graphql/"

auth_chat = {}

class Auth: 

    def index(update, context):
        chat_id = update.message.chat_id

        update.message.reply_text("Ok, vamos te autenticar!")
        update.message.reply_text("Caso deseje interromper o processo digite /cancelar")
        update.message.reply_text("Por favor, informe seu CPF:")

        auth_chat[chat_id] = {}

        return CPF_AUTH

    def cpf(update, context):


        cpf = update.message.text
        chat_id = update.message.chat_id

        if not ValidateForm.cpf(cpf, update):
            return CPF_AUTH

        cpf = ValidateForm.cpf(cpf, update)

        auth_chat[chat_id]['cpf'] = cpf

        update.message.reply_text('Grave um áudio de no mínimo 1 segundo dizendo "Juro que sou eu"')

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

        auth_chat[chat_id]['voice_mfcc'] = mfcc_data

        response = Auth.authenticate(chat_id)

        valid = response['data']['voiceBelongsUser']

        if valid:
            update.message.reply_text('Autenticado(a) com sucesso!')
        else:
            update.message.reply_text('Falha na autenticação!')

        auth_chat[chat_id] = {}

        return ConversationHandler.END

    def end(update, context):
        chat_id = update.message.chat_id
        update.message.reply_text('Autenticação cancelada!')

        auth_chat[chat_id] = {}

        return ConversationHandler.END

    def authenticate(chat_id):
        query = """
        query voiceBelongsUser(
            $cpf: String!,
            $mfccData: String
        ){
            voiceBelongsUser(cpf: $cpf, mfccData: $mfccData)
        }
        """

        variables = {
                'cpf': auth_chat[chat_id]['cpf'],
                'mfccData': auth_chat[chat_id]['voice_mfcc']
        }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        return response.json()

