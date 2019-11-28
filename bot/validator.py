"""
Validate user input
"""

import logging
import requests
from settings import LOG_NAME, PATH, API_TOKEN

logger = logging.getLogger(LOG_NAME)

class ValidateForm:
    """
    Validate user information functions
    """
    def name(name, update):
        """
        Validate user name
        """
        if("nome" in name.lower()):
            logger.error("Resident informing his name in a sentence - asking again")
            update.message.reply_text('Por favor, digite apenas o seu nome:')
            return False
        if(any(i.isdigit() for i in name)):
            logger.error("Numbers in name - asking again")
            update.message.reply_text(
                'Por favor, não digite números, tente novamente:')
            return False
        if("@" in name or len(name) < 3):
            logger.error("Email instead name - asking again")
            update.message.reply_text(
                'Neste momento é hora de digitar o seu nome, tente novamente:')
            return False
        if(len(name) > 80):
            looging.error("Name out of range - asking again")
            update.message.reply_text(
                'Nome excedeu tamanho máximo (80), tente novamente:')
            return False

        return True

    def phone(phone, contact, update):
        """
        Validate user phone
        """
        if(phone is not None):
            if("-" in phone):
                logger.debug("Removing dashes from phone")
                phone = phone.replace('-', '')

            if(" " in phone):
                logger.debug("Removing white-spaces from phone")
                phone = phone.replace(' ', '')

            if("+" in phone):
                logger.debug("Removing '+' from phone")
                phone = phone.replace('+', '')

            if(any(i.isalpha() for i in phone)):
                logger.error("Alphabetic character in phone - asking again")
                update.message.reply_text(
                    'Por favor, digite seu telefone corretamente:')
                return False

            if(len(phone) > 15):
                logger.error("Phone out of range - asking again")
                update.message.reply_text(
                    'Telefone excedeu tamanho máximo (15), tente novamente:')
                return False

        else:
            phone = contact.phone_number
            phone = phone.replace('+', '')

        return phone

    def email(email, update):
        """
        Validate e-mail
        """
        if("@" not in email or " " in email or len(email) < 4 or "." not in email):
            logger.error("Invalid email - asking again")
            update.message.reply_text('Por favor, digite um email válido:')
            return False

        if(len(email) > 90):
            logger.error("Email out of range - asking again")
            update.message.reply_text(
                'Email excedeu tamanho máximo (90), tente novamente:')
            return False

        return True

    def cpf(cpf, update):
        """
        Validate user cpf
        """
        if(len(cpf) > 11 and cpf[3] == "." and cpf[7] == "." and cpf[11] == "-"):
            logger.debug("Removing dots and dash from CPF")
            cpf = cpf.replace('.', '').replace('-', '')
            logger.debug("Removing dots and dash from CPF")

        if(any(i.isalpha() for i in cpf) or "." in cpf or "-" in cpf or len(cpf) != 11):
            logger.error("CPF in wrong formatation - asking again")
            update.message.reply_text(
                'Por favor, digite o CPF com os 11 digitos: (Ex: 123.456.789-10)'
            )
            logger.error("CPF in wrong formatation - asking again")
            return False

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
        if((int(cpf[9]) != 0 and authCPF_J != 0 and
            authCPF_J != 1) and (int(cpf[9]) != (11 - authCPF_J))):
            update.message.reply_text('CPF inválido, tente novamente:')
            logger.error("Invalid CPF - asking again")
            return False

        if((int(cpf[10]) != 0 and authCPF_K != 0 and
            authCPF_K != 1) and (int(cpf[10]) != (11 - authCPF_K))):
            logger.error("Invalid CPF - asking again")
            update.message.reply_text('CPF inválido, tente novamente:')
            return False

        return cpf

    def block(block, update):
        """
        Validate apartment block
        """
        if("bloco" in block.lower() or " " in block):
            logger.error("Resident informing the block number in a sentence - asking again")
            update.message.reply_text(
                'Por favor, digite apenas o bloco: (Ex: 1)')
            return False

        if(len(block) > 4):
            logger.error("Block number out of range - asking again")
            update.message.reply_text('Digte um bloco de até 4 caracteres:')
            return False

        return True

    def apartment(apartment, update):
        """
        Validate apartment number
        """
        if(any(i.isalpha() for i in apartment) or " " in apartment):
            loggin.error("Alphabetic character in apartment number - asking again")
            update.message.reply_text(
                'Por favor, digite apenas o apartamento: (Ex: 101)')
            return False

        if(len(apartment) > 6):
            logger.error("Apartment out of range - asking again")
            update.message.reply_text(
                'Digite um apartamente de até 6 caracteres:')
            return False

        return True

    def audio_has_valid_duration(voice_register, update):
        """
        Validate voice duration
        """
        if((voice_register.duration) < 1.0):
            logger.error("Audio too short - asking again")
            update.message.reply_text(
                'Muito curto... O áudio deve ter no mínimo 1 segundo de duração.')
            update.message.reply_text('Por favor, grave novamente:')
            return False
        elif((voice_register.duration) > 4.0):
            logger.error("Audio too long - asking again")
            update.message.reply_text(
                'Muito grande... O áudio deve ter no máximo 4 segundos de duração.')
            update.message.reply_text('Por favor, grave novamente:')
            return False

        return True

    def audio_has_good_volume(audio_data, update):
        '''
        Check audio volume
        '''
        logger.debug('Checking audio volume')

        try:
            query = '''
            query audioHasGoodVolume ($audioData: [Float]!, $audioSamplerate: Int!) {
                audioHasGoodVolume (audioData: $audioData, audioSamplerate: $audioSamplerate)
            }
            '''

            variables = {
                'audioData': audio_data,
                'audioSamplerate': 16000
            }

            headers = {
                'Authorization': 'JWT %s' % API_TOKEN
            }

            response = requests.post(PATH, headers=headers, json={'query':query, 'variables':variables}).json()
            print(response)

            if response["data"]["audioHasGoodVolume"] == False:
                logger.error("Audio volume is not good - asking for another audio")
                update.message.reply_text('Ixi! Não consegui escutar direito você falando.')
                update.message.reply_text('Por favor, fale um pouquinho mais alto.')

                return False
        except:
            logger.exception('An exception occurred')

        return True

    def boolean_value(value, update):
        """
        Convert user input in boolean value
        """
        if(value != "Sim" and value != "Não"):
            logger.error("Boolean value isn't in valid format")
            update.message.reply_text('Você deve apenas apertar o botão "Sim" ou "Não".')
            return False

        return True

    def number(value, update):
        """
        Validate if value is a number
        """
        if not str.isdigit(value):
            logger.error("Incorrect format number")
            update.message.reply_text("Comando incorreto. Digite no formato /numero")
            return False

        return True
