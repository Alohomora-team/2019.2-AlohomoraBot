from checks import check_email, check_cpf, check_block, check_apartment
from python_speech_features import mfcc
from scipy.io.wavfile import read
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
import json
import numpy
import requests
import subprocess
import os

NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, VOICE_REGISTER, REPEAT_VOICE = range(8)

PATH = os.environ['API_PATH']

chat = {}

def register(update, context):
    chat_id = update.message.chat_id

    update.message.reply_text('Ok, vamos iniciar o cadastro!')
    update.message.reply_text('Caso deseje interromper o processo digite /cancelar')
    update.message.reply_text('Nome:')

    chat[chat_id] = {}

    return NAME

def name(update, context):
    chat_id = update.message.chat_id
    name = update.message.text

    if("nome" in name.lower()):
        update.message.reply_text('Por favor, digite apenas o seu nome:')
        return NAME
    if(any(i.isdigit() for i in name)):
        update.message.reply_text('Por favor, não digite números no nome, tente novamente:')
        return NAME
    if("@" in name or len(name)<3):
        update.message.reply_text('Neste momento é hora de digitar o seu nome, tente novamente:')
        return NAME
    if(len(name) > 80):
        update.message.reply_text('Nome excedeu tamanho máximo (80), tente novamente:')
        return NAME

    chat[chat_id]['name'] = name

    contact_keyboard = KeyboardButton('Enviar meu número de telefone', request_contact=True)
    custom_keyboard = [[ contact_keyboard ]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text('Telefone:', reply_markup=reply_markup)

    return PHONE

def phone(update, context):
    chat_id = update.message.chat_id

    if(update.message.text is not None):
        phone = update.message.text

        if("-" in phone):
            phone = phone.replace('-','')

        if(" " in phone):
            phone = phone.replace(' ','')

        if("+" in phone):
            phone = phone.replace('+','')

        if(any(i.isalpha() for i in phone)):
            update.message.reply_text('Por favor, digite seu telefone corretamente:')
            return PHONE

        if(len(phone) > 15):
            update.message.reply_text('Telefone excedeu tamanho máximo (15), tente novamente:')
            return PHONE

    else:
        contact = update.effective_message.contact
        phone = contact.phone_number
        phone = phone.replace('+','')

    chat[chat_id]['phone'] = phone

    update.message.reply_text('Email:')

    return EMAIL

def email(update, context):
    chat_id = update.message.chat_id
    email = update.message.text

    if("@" not in email or " " in email or len(email)<4 or "." not in email):
        update.message.reply_text('Por favor, digite um email válido:')
        return EMAIL

    if(len(email) > 90):
        update.message.reply_text('Email excedeu tamanho máximo (90), tente novamente:')
        return EMAIL

    chat[chat_id]['email'] = email

    check = check_email(chat, chat_id)

    if 'errors' not in check.keys():
        update.message.reply_text('Já existe um morador com este email, tente novamente:')
        return EMAIL

    update.message.reply_text('CPF:')

    return CPF

def cpf(update, context):
    chat_id = update.message.chat_id
    cpf = update.message.text

    if(len(cpf) > 11 and cpf[3] == "." and cpf[7] == "." and cpf[11] == "-"):
        cpf = cpf.replace('.','').replace('-','')

    if(any(i.isalpha() for i in cpf) or "." in cpf or "-" in cpf or len(cpf) != 11):
        update.message.reply_text('Por favor, digite o CPF com os 11 digitos: (Ex: 123.456.789-10)')
        return CPF

    authCPF_J = (int(cpf[0])*10 +
                 int(cpf[1])*9 +
                 int(cpf[2])*8 +
                 int(cpf[3])*7 +
                 int(cpf[4])*6 +
                 int(cpf[5])*5 +
                 int(cpf[6])*4 +
                 int(cpf[7])*3 +
                 int(cpf[8])*2) % 11

    authCPF_K = (int(cpf[0])*11 +
                 int(cpf[1])*10 +
                 int(cpf[2])*9 +
                 int(cpf[3])*8 +
                 int(cpf[4])*7 +
                 int(cpf[5])*6 +
                 int(cpf[6])*5 +
                 int(cpf[7])*4 +
                 int(cpf[8])*3 +
                 int(cpf[9])*2) % 11

    # Validating CPF
    if((int(cpf[9]) != 0 and authCPF_J != 0 and authCPF_J != 1) and (int(cpf[9]) != (11 - authCPF_J))):
        update.message.reply_text('CPF inválido, tente novamente:')
        return CPF

    if((int(cpf[10]) != 0 and authCPF_K != 0 and authCPF_K != 1) and (int(cpf[10]) != (11 - authCPF_K))):
        update.message.reply_text('CPF inválido, tente novamente:')
        return CPF

    chat[chat_id]['cpf'] = cpf

    check = check_cpf(chat, chat_id)

    if 'errors' not in check.keys():
        update.message.reply_text('Já existe um morador com este CPF, tente novamente:')
        return CPF

    update.message.reply_text('Bloco:')

    return BLOCK

def block(update, context):
    chat_id = update.message.chat_id
    block = update.message.text

    if("bloco" in block.lower() or " " in block):
        update.message.reply_text('Por favor, digite apenas o bloco: (Ex: 1)')
        return BLOCK

    if(len(block) > 4):
        update.message.reply_text('Digte um bloco de até 4 caracteres:')
        return BLOCK

    chat[chat_id]['block'] = block

    check = check_block(chat, chat_id)

    if 'errors' in check.keys():
        update.message.reply_text('Por favor, digite um bloco existente:')
        return BLOCK

    update.message.reply_text('Apartamento:')

    return APARTMENT

def apartment(update, context):
    chat_id = update.message.chat_id
    apartment = update.message.text

    if(any(i.isalpha() for i in apartment) or " " in apartment):
        update.message.reply_text('Por favor, digite apenas o apartamento: (Ex: 101)')
        return APARTMENT

    if(len(apartment) > 6):
        update.message.reply_text('Digite um apartamente de até 6 caracteres:')
        return APARTMENT

    chat[chat_id]['apartment'] = apartment

    check = check_apartment(chat, chat_id)

    if 'errors' in check.keys():
        update.message.reply_text('Por favor, digite um apartamento existente:')
        return APARTMENT

    update.message.reply_text('Vamos agora cadastrar a sua voz! Grave uma breve mensagem de voz dizendo "Juro que sou eu"')

    return VOICE_REGISTER

def voice_register(update, context):
    chat_id = update.message.chat_id
    voice_register = update.message.voice

    if((voice_register.duration)<1.0):
        update.message.reply_text('Muito curto...O áudio deve ter 1 segundo de duração.')
        update.message.reply_text('Por favor, grave novamente:')
        return VOICE_REGISTER
    elif((voice_register.duration)>2.0):
        update.message.reply_text('Muito grande...O áudio deve ter 2 segundo de duração.')
        update.message.reply_text('Por favor, grave novamente:')
        return VOICE_REGISTER
    else:
        update.message.reply_text('Ótimo!')

    f_reg = voice_register.get_file()

    src = f_reg.download()
    dest = src.split('.')[0] + ".wav"

    subprocess.run(['ffmpeg', '-i', src, dest])

    samplerate, voice_data = read(dest)

    mfcc_data = mfcc(voice_data, samplerate=samplerate, nfft=1200, winfunc=numpy.hamming)
    mfcc_data = mfcc_data.tolist()
    mfcc_data = json.dumps(mfcc_data)

    chat[chat_id]['voice_reg'] = None
    chat[chat_id]['voice_mfcc'] = mfcc_data

    # Repeat and confirm buttons
    repeat_keyboard = KeyboardButton('Repetir')
    confirm_keyboard = KeyboardButton('Confirmar')
    keyboard = [[repeat_keyboard],[confirm_keyboard]]
    choice = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Escute o seu áudio e confirme se está com boa qualidade', reply_markup = choice)

    return REPEAT_VOICE

def repeat_voice(update, context):
    chat_id = update.message.chat_id
    choice = update.message.text

    if choice == "Repetir":
        update.message.reply_text('Por favor, grave novamente:')
        return VOICE_REGISTER

    response = register_user(chat_id)

    if(response.status_code == 200 and 'errors' not in response.json().keys()):
        update.message.reply_text('Morador cadastrado no sistema!')
    else:
        update.message.reply_text('Falha ao cadastrar no sistema!')

    chat[chat_id] = {}

    return ConversationHandler.END

def end(update, context):
    chat_id = update.message.chat_id

    update.message.reply_text('Cadastro cancelado!')

    chat[chat_id] = {}

    return ConversationHandler.END


def register_user(chat_id):
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
            'mfccData': chat[chat_id]['voice_mfcc']
            }

    response = requests.post(PATH, json={'query':query, 'variables':variables})

    return response
