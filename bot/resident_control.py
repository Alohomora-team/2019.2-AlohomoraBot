import json
import logging
import subprocess
import numpy
import requests
from python_speech_features import mfcc
from scipy.io.wavfile import read
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from settings import CPF_AUTH, VOICE_AUTH, HANDLE_VISITORS_PENDING, CHOOSE_AUTH
from settings import PATH, LOG_NAME
from validator import ValidateForm
from helpers import format_datetime

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

        pwd_keyboard = KeyboardButton('Senha')
        voice_keyboard = KeyboardButton('Voz')
        keyboard = [[pwd_keyboard], [voice_keyboard]]
        choice = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('De que maneira deseja se autenticar?', reply_markup=choice)

        return CHOOSE_AUTH

    def choose_auth(update, context):
        chat_id = update.message.chat_id
        choice = update.message.text

        if choice == "Senha":
            CHAT[chat_id]['choice'] = choice
            LOGGER.debug(f"'1-choice': '{CHAT[chat_id]['choice']}'")

            LOGGER.info("Replied to authenticate by password")
            update.message.reply_text('Ok! Informe sua senha:')
            LOGGER.info("Requesting password")
            return PASSWORD_AUTH
        elif choice == "Voz":
            CHAT[chat_id]['choice'] = choice
            LOGGER.debug(f"'2-choice': '{CHAT[chat_id]['choice']}'")

            LOGGER.info("Replied to authenticate by voice")
            update.message.reply_text('Grave um áudio de no mínimo 1 segundo dizendo "Juro que sou eu"')
            LOGGER.info("Requesting voice audio")
            return VOICE_AUTH
        else:
            CHAT[chat_id]['choice'] = choice
            LOGGER.debug(f"'3-choice': '{CHAT[chat_id]['choice']}'")

            update.message.reply_text('Por favor, apenas aperte um dos botões.')
            return CHOOSE_AUTH

        CHAT[chat_id]['choice'] = choice
        LOGGER.debug(f"'4-choice': '{CHAT[chat_id]['choice']}'")

    def password(update, context):
        pass

    @staticmethod
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

    @staticmethod
    def index(update, context):
        chat_id = update.message.chat_id
        reply = update.message.text

        if 'Remover' in reply:

            if reply == 'Remover todas':
                LOGGER.info('resident request remove all visitors entries pending')

                response = HandleEntryVisitor.delete_entries_pending(chat_id)

                status = response['data']['deleteEntriesVisitorsPending']

                if status['deleted']:
                    LOGGER.info('all visitor entries pending is removed.')
                    update.message.reply_text('Todos as entradas pendentes foram removidas.')

                else:
                    LOGGER.info('error in delete visitors entries')
                    update.message.reply_text('Erro ao deletar entradas pendentes.')

            else:
                LOGGER.info('resident request remove a specific visitor entry pending')

                #find entry_id in reply
                remove_entry_by_id = [int(number) for number in reply.split() if number.isdigit()]
                LOGGER.debug(remove_entry_by_id[0])

                CHAT[chat_id]['remove_entry_by_id'] = remove_entry_by_id[0]

                response = HandleEntryVisitor.delete_entry_pending(chat_id)

                status = response['data']['deleteEntryVisitorPending']

                if status['deleted']:
                    LOGGER.info('A single visitor entry pending is removed.')

                    update.message.reply_text(
                        'A entrada pendente foi removida.'+
                        '\nPara liberar ou remover alguma entrada, digite o respectivo código\n'+
                        'Para remover uma entrada especifica, escreva "Remover + numero da entrada"'
                        )

                    return HANDLE_VISITORS_PENDING

                else:
                    LOGGER.info('error in delete visitor entry')
                    update.message.reply_text('Erro ao deletar entrada pendente.')


            return ConversationHandler.END


        elif reply == 'Cancelar':
            LOGGER.info('resident end conversation')

            return HandleEntryVisitor.end(update, context)

        if not ValidateForm.number(reply, update):
            return HANDLE_VISITORS_PENDING

        CHAT[chat_id]['entry_id'] = reply

        status = HandleEntryVisitor.allow_entry(chat_id)

        if 'errors' not in status.keys():
            LOGGER.info('entry visitor updated successfully')

            update.message.reply_text(
                'A entrada foi aceita'
                '\nPara liberar alguma entrada, digite o respectivo código\n'
                'Para remover uma entrada especifica, escreva "Remover + numero da entrada"'
            )

        else:
            LOGGER.info('entry visitor updated error')
            update.message.reply_text('Ocorreu um erro ao aceitar a entrada.')

        return HANDLE_VISITORS_PENDING

    @staticmethod
    def get_resident_apartment(chat_id):
        LOGGER.debug("Getting resident block and apartment")
        query = """
            query resident(
                $cpf: String!
            ){
                resident(
                    cpf: $cpf
                ){
                    completeName
                    apartment {
                        id
                        number
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

    @staticmethod
    def get_entries_pending(chat_id):
        LOGGER.debug("Sending query to get entries pending of visitors")
        query = """
            query entriesVisitorsPending(
                $apartmentId: String!
            ) {
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
            'apartmentId': CHAT[chat_id]['apartment']['id'],
        }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response.json()

    @staticmethod
    def allow_entry(chat_id):
        LOGGER.info("Updating entry")
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
            'entryId': CHAT[chat_id]['entry_id'],
        }

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        LOGGER.debug(f"Response: {response.json()}")

        return response.json()

    @staticmethod
    def delete_entries_pending(chat_id):
        LOGGER.info("Deleting all entries visitors pending")
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
            'apartmentId': CHAT[chat_id]['apartment']['id'],
        }

        response = requests.post(PATH, json={'query': query, 'variables': variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response.json()

    @staticmethod
    def delete_entry_pending(chat_id):
        LOGGER.debug("Deleting a specific entry visitor pending")
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
            'entryId': CHAT[chat_id]['remove_entry_by_id'],
        }

        response = requests.post(PATH, json={'query': query, 'variables': variables})

        return response.json()

    @staticmethod
    def end(update, context):
        chat_id = update.message.chat_id
        update.message.reply_text('Comando de autorização cancelado!')
        LOGGER.info("Canceling command")

        CHAT[chat_id] = {}
        LOGGER.debug(f"data['{chat_id}']: {CHAT[chat_id]}")

        return ConversationHandler.END
