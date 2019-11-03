import logging
from settings import LOG_NAME

LOGGER = logging.getLogger(LOG_NAME)

class ValidateForm:

    @staticmethod
    def name(name, update):
        if "nome" in name.lower():
            update.message.reply_text('Por favor, digite apenas o seu nome:')
            LOGGER.error("Resident informing his name in a sentence - asking again")
            return False

        if any(i.isdigit() for i in name):
            LOGGER.error("Numbers in name - asking again")
            update.message.reply_text(
                'Por favor, não digite números no nome, tente novamente:'
            )

            return False

        if "@" in name or len(name) < 3:
            LOGGER.error("Email instead name - asking again")
            update.message.reply_text(
                'Neste momento é hora de digitar o seu nome, tente novamente:'
            )

            return False

        if len(name) > 80:
            LOGGER.error("Name out of range - asking again")
            update.message.reply_text(
                'Nome excedeu tamanho máximo (80), tente novamente:'
            )

            return False

        return True

    @staticmethod
    def phone(phone, contact, update):
        if phone is not None:
            if "-" in phone:
                LOGGER.debug("Removing dashes from phone")
                phone = phone.replace('-', '')

            if " " in phone:
                LOGGER.debug("Removing white-spaces from phone")
                phone = phone.replace(' ', '')

            if "+" in phone:
                LOGGER.debug("Removing '+' from phone")
                phone = phone.replace('+', '')

            if any(i.isalpha() for i in phone):
                LOGGER.error("Alphabetic character in phone - asking again")
                update.message.reply_text(
                    'Por favor, digite seu telefone corretamente:'
                )

                return False

            if len(phone) > 15:
                LOGGER.error("Phone out of range - asking again")
                update.message.reply_text(
                    'Telefone excedeu tamanho máximo (15), tente novamente:'
                )

                return False

        else:
            phone = contact.phone_number
            phone = phone.replace('+', '')

        return phone

    @staticmethod
    def email(email, update):
        if "@" not in email or " " in email or len(email) < 4 or "." not in email:
            LOGGER.error("Invalid email - asking again")
            update.message.reply_text('Por favor, digite um email válido:')

            return False

        if len(email) > 90:
            LOGGER.error("Email out of range - asking again")
            update.message.reply_text(
                'Email excedeu tamanho máximo (90), tente novamente:'
            )

            return False

        return True

    @staticmethod
    def cpf(cpf, update):
        if len(cpf) > 11 and cpf[3] == "." and cpf[7] == "." and cpf[11] == "-":
            LOGGER.debug("Removing dots and dash from CPF")
            cpf = cpf.replace('.', '').replace('-', '')
            LOGGER.debug("Removing dots and dash from CPF")

        if any(i.isalpha() for i in cpf) or "." in cpf or "-" in cpf or len(cpf) != 11:
            LOGGER.error("CPF in wrong formatation - asking again")
            update.message.reply_text(
                'Por favor, digite o CPF com os 11 digitos: (Ex: 123.456.789-10)'
            )
            LOGGER.error("CPF in wrong formatation - asking again")

            return False

        aCPF_J = (int(cpf[0])*10 +
                  int(cpf[1])*9 +
                  int(cpf[2])*8 +
                  int(cpf[3])*7 +
                  int(cpf[4])*6 +
                  int(cpf[5])*5 +
                  int(cpf[6])*4 +
                  int(cpf[7])*3 +
                  int(cpf[8])*2) % 11

        aCPF_K = (int(cpf[0])*11 +
                  int(cpf[1])*10 +
                  int(cpf[2])*9 +
                  int(cpf[3])*8 +
                  int(cpf[4])*7 +
                  int(cpf[5])*6 +
                  int(cpf[6])*5 +
                  int(cpf[7])*4 +
                  int(cpf[8])*3 +
                  int(cpf[9])*2) % 11

        if (int(cpf[9]) != 0 and aCPF_J != 0 and aCPF_J != 1) and int(cpf[9]) != (11 - aCPF_J):
            update.message.reply_text('CPF inválido, tente novamente:')
            LOGGER.error("Invalid CPF - asking again")

            return False

        if (int(cpf[10]) != 0 and aCPF_K != 0 and aCPF_K != 1) and (int(cpf[10]) != (11 - aCPF_K)):
            LOGGER.error("Invalid CPF - asking again")
            update.message.reply_text('CPF inválido, tente novamente:')

            return False

        return cpf

    @staticmethod
    def block(block, update):
        if "bloco" in block.lower() or " " in block:
            LOGGER.error("Resident informing the block number in a sentence - asking again")
            update.message.reply_text(
                'Por favor, digite apenas o bloco: (Ex: 1)')

            return False

        if len(block) > 4:
            LOGGER.error("Block number out of range - asking again")
            update.message.reply_text('Digte um bloco de até 4 caracteres:')

            return False

        return True

    @staticmethod
    def apartment(apartment, update):
        if any(i.isalpha() for i in apartment) or " " in apartment:
            LOGGER.error("Alphabetic character in apartment number - asking again")
            update.message.reply_text(
                'Por favor, digite apenas o apartamento: (Ex: 101)')

            return False

        if len(apartment) > 6:
            LOGGER.error("Apartment out of range - asking again")
            update.message.reply_text(
                'Digite um apartamente de até 6 caracteres:')

            return False

        return True

    @staticmethod
    def voice(voice_register, update):
        if voice_register.duration < 1.0:
            LOGGER.error("Audio too short - asking again")
            update.message.reply_text(
                'Muito curto...O áudio deve ter 1 segundo de duração.')
            update.message.reply_text('Por favor, grave novamente:')

            return False

        if voice_register.duration > 2.0:
            LOGGER.error("Audio too long - asking again")
            update.message.reply_text(
                'Muito grande...O áudio deve ter 2 segundo de duração.')
            update.message.reply_text('Por favor, grave novamente:')

            return False

        return True

    @staticmethod
    def audio_speaking_name(audio, update):
        LOGGER.debug('\tValidating audio duration ...')

        if audio.duration < 0.9:
            LOGGER.error('\t\tToo short audio. Trying again.')
            update.message.reply_text('Seu áudio foi muito curto. Por favor, grave novamente.')
            return False

        if audio.duration > 3.1:
            LOGGER.error('\t\tToo long audio. Trying again.')
            update.message.reply_text('Seu áudio foi muito longo. Por favor, grave novamente.')
            return False

        LOGGER.debug('\t\tAudio is ok.\n')
        return True

    def boolean_value(value, update):
        if(value != "Sim" and value != "Não"):
            LOGGER.error("Boolean value isn't in valid format")
            update.message.reply_text('Você deve apenas apertar o botão "Sim" ou "Não".')
            return False

        return True
