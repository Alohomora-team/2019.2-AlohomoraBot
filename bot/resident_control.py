import json
import logging
import subprocess
import numpy
#import os
import requests
from python_speech_features import mfcc
from scipy.io.wavfile import read
from settings import CPF_AUTH, VOICE_AUTH, SHOW_VISITORS_PENDING
from settings import PATH, LOG_NAME
from telegram.ext import ConversationHandler
from validator import ValidateForm

LOGGER = logging.getLogger(LOG_NAME)

CHAT = {}

class Auth:

    @staticmethod
    def index(update, context):
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
        chat_id = update.message.chat_id
        voice_auth = update.message.voice

        if not ValidateForm.voice(voice_auth, update):
            return VOICE_AUTH

        file_auth = voice_auth.get_file()

        src = file_auth.download()
        dest = src.split('.')[0] + ".wav"

        subprocess.run(['ffmpeg', '-i', src, dest], check=True)

        samplerate, voice_data = read(dest)

        mfcc_data = mfcc(voice_data, samplerate=samplerate, nfft=1200, winfunc=numpy.hamming)
        mfcc_data = mfcc_data.tolist()
        mfcc_data = json.dumps(mfcc_data)

        CHAT[chat_id]['voice_mfcc'] = mfcc_data
        LOGGER.debug(
    f"'auth-voice-mfcc':'{CHAT[chat_id]['voice_mfcc'][:1]}...{CHAT[chat_id]['voice_mfcc'][-1:]}'"
        )

        response = Auth.authenticate(chat_id)

        valid = response['data']['voiceBelongsResident']

        if valid:
            LOGGER.info("resident has been authenticated")
            update.message.reply_text('Autenticado(a) com sucesso!')

            response = HandleEntryVisitor.get_resident_apartment(chat, chat_id)

            resident = response['data']['resident']
            apartment = resident['apartment']
            block = apartment['block']

            update.message.reply_text(apartment)
            update.message.reply_text(block)

            CHAT[chat_id]['block'] = block['number']
            CHAT[chat_id]['apartment'] = apartment['number']

            HandleEntryVisitor.get_entries_pending(chat, chat_id)

        else:
            LOGGER.error("Authentication failed")
            update.message.reply_text('Falha na autenticação!')


        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return ConversationHandler.END

    @staticmethod
    def end(update, context):
        chat_id = update.message.chat_id
        update.message.reply_text('Autenticação cancelada!')
        LOGGER.info("Canceling authentication")

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return ConversationHandler.END

    @staticmethod
    def authenticate(chat_id):
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

class HandleEntryVisitor:

    def index(update, context):
        return

    def get_resident_apartment(chat, chat_id):
        LOGGER.debug("Getting resident block and apartment")
        query = """
        query resident($cpf: String!){
            resident(cpf: $cpf){
                completeName
                apartment {
                    number
                    block {
                        number
                    }
                }
            }
        }
        """

        variables = {
            'cpf': CHAT[chat_id]['cpf']
            }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response.json()

    def get_entries_pending(chat, chat_id):
        LOGGER.debug("Sending query to get entries pending of visitors")
        query = """
        query entriesVisitorsPending($blockNumber: String!, $apartmentNumber: String!){
            entriesVisitorsPending(blockNumber: $blockNumber, apartmentNumber: $apartmentNumber){
                visitor {
                    completeName
                    cpf
                }
                date
            }
        }
        """

        variables = {
            'blockNumber': CHAT[chat_id]['block'],
            'apartmentNumber': CHAT[chat_id]['apartment']
            }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response.json()
