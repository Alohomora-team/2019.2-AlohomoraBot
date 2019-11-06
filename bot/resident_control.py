from python_speech_features import mfcc
from scipy.io.wavfile import read
from settings import CPF_AUTH, VOICE_AUTH, HANDLE_VISITORS_PENDING
from settings import PATH, LOG_NAME
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from validator import ValidateForm
from helpers import format_datetime
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
        update.message.reply_text("Ok. Mas antes, você precisa se autenticar!")
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
            logger.info("resident has been authenticated")
            update.message.reply_text('Autenticado(a) com sucesso!')
            
            response = HandleEntryVisitor.get_resident_apartment(chat, chat_id)

            resident = response['data']['resident']
            apartment = resident['apartment']
            
            chat[chat_id]['apartment'] = apartment

            response = HandleEntryVisitor.get_entries_pending(chat, chat_id)

            entries = response['data']['entriesVisitorsPending']

            if entries:
                update.message.reply_text('Você possui entrada(s) pendente(s):')
                logger.info("Showing visitors pending to resident")
            else:
                update.message.reply_text('Você não possui entrada(s) pendente(s)')
                logger.info("Apartment don`t have pending entries")
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
            keyboard = [[remove_keyboard],[cancel_keyboard]]
            response = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            update.message.reply_text('Para liberar ou remover alguma entrada, digite o respectivo código'+
            '\nPara remover uma entrada especifica, escreva "Remover + seu respectivo código"', reply_markup=response)

            return HANDLE_VISITORS_PENDING

        logger.error("Authentication failed")
        update.message.reply_text('Falha na autenticação!')


        return HandleEntryVisitor.end(update, context)

    def authenticate(chat_id):
        logger.info("Authenticating resident")
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


class HandleEntryVisitor: 

    def index(update, context):
        chat_id = update.message.chat_id
        reply = update.message.text
        
        if 'Remover' in reply: 

            if reply == 'Remover todas':
                logger.info('resident request remove all visitors entries pending')

                response = HandleEntryVisitor.delete_entries_pending(chat, chat_id)

                status = response['data']['deleteEntriesVisitorsPending']

                if status['deleted']:
                    logger.info('all visitor entries pending is removed.')
                    update.message.reply_text('Todos as entradas pendentes foram removidas.')

                else: 
                    logger.info('error in delete visitors entries')
                    update.message.reply_text('Erro ao deletar entradas pendentes.')

            else:
                logger.info('resident request remove a specific visitor entry pending')

                #find entry_id in reply
                remove_entry_by_id = [int(number) for number in reply.split() if number.isdigit()]
                logger.debug(remove_entry_by_id[0])

                chat[chat_id]['remove_entry_by_id'] = remove_entry_by_id[0]

                response = HandleEntryVisitor.delete_entry_pending(chat, chat_id)

                status = response['data']['deleteEntryVisitorPending']

                if status['deleted']:
                    logger.info('A single visitor entry pending is removed.')

                    update.message.reply_text('A entrada pendente foi removida.')
                    update.message.reply_text('Para liberar ou remover alguma entrada, digite o respectivo código')
                    update.message.reply_text('Para remover uma entrada especifica, escreva "Remover + numero da entrada"')

                    return HANDLE_VISITORS_PENDING

                else: 
                    logger.info('error in delete visitor entry')
                    update.message.reply_text('Erro ao deletar entrada pendente.')


            return ConversationHandler.END

        
        elif reply == 'Cancelar':
            logger.info('resident end conversation')

            return HandleEntryVisitor.end(update, context)

        if not ValidateForm.number(reply, update):
            return HANDLE_VISITORS_PENDING

        chat[chat_id]['entry_id'] = reply

        status = HandleEntryVisitor.allow_entry(chat, chat_id)

        if 'errors' not in status.keys():
            logger.info('entry visitor updated successfully')

            update.message.reply_text('A entrada foi aceita')
            update.message.reply_text('Para liberar alguma entrada, digite o respectivo código')
            update.message.reply_text('Para remover uma entrada especifica, escreva "Remover + numero da entrada"')
    
        logger.info('entry visitor updated error')
        update.message.reply_text('Ocorreu um erro ao aceitar a entrada.')

        return HANDLE_VISITORS_PENDING

    def get_resident_apartment(chat, chat_id):
        logger.debug("Getting resident block and apartment")
        query = """
        query resident($cpf: String!){
            resident(cpf: $cpf){
                completeName
                apartment {
                    id
                    number
                }
            }
        }
        """

        variables = {
            'cpf': chat[chat_id]['cpf']
            }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        logger.debug(f"Response: {response.json()}")

        return response.json()

    def get_entries_pending(chat, chat_id):
        logger.debug("Sending query to get entries pending of visitors")
        query = """
        query entriesVisitorsPending($apartmentId: String!) {
            entriesVisitorsPending(
                apartmentId: $apartmentId, 
            ){
                id
                date
                pending
                visitor {
                    id
                    completeName
                    cpf
                }
            }
        }
        """

        variables = {
            'apartmentId': chat[chat_id]['apartment']['id'],
            }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        logger.debug(f"Response: {response.json()}")

        return response.json()

    def allow_entry(chat, chat_id):
        logger.info("Updating entry")
        query = """
        mutation updateEntryVisitorPending(
            $entryId: String!
            ){
            updateEntryVisitorPending(
                entryId: $entryId
            ){
                entryId
                entryVisitorPending
            }
        }
        """

        variables = {
            'entryId': chat[chat_id]['entry_id'],
            }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        logger.debug(f"Response: {response.json()}")

        return response.json()

    def delete_entries_pending(chat, chat_id):
        logger.info("Deleting all entries visitors pending")
        query = """
        mutation deleteEntriesVisitorsPending(
            $apartmentId: String!
            ){
            deleteEntriesVisitorsPending (
                apartmentId: $apartmentId,
            ) {
                deleted
            }
        }
        """

        variables = {
            'apartmentId': chat[chat_id]['apartment']['id'],
            }

        response = requests.post(PATH, json={'query': query, 'variables': variables})
        logger.debug(f"Response: {response.json()}")

        return response.json()

    def delete_entry_pending(chat, chat_id):
        logger.debug("Deleting a specific entry visitor pending")
        query = """
        mutation deleteEntryVisitorPending(
            $entryId: String!
        ){
            deleteEntryVisitorPending (
                entryId: $entryId
            ){
                deleted
            }
        }
        """

        variables = {
            'entryId': chat[chat_id]['remove_entry_by_id'],
            }

        response = requests.post(PATH, json={'query': query, 'variables': variables})

        return response.json()

    def end(update, context):
        chat_id = update.message.chat_id
        update.message.reply_text('Comando de autorização cancelado!')
        logger.info("Canceling command")

        chat[chat_id] = {}
        logger.debug(f"data['{chat_id}']: {chat[chat_id]}")

        return ConversationHandler.END

       


