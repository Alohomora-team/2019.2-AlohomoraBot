import logging
import requests
from settings import PATH, LOG_NAME

LOGGER = logging.getLogger(LOG_NAME)

class CheckCondo:

    @staticmethod
    def block(chat, chat_id):
        LOGGER.debug("Checking if the informed block exists in database")
        query = """
        query block($number: String!){
            block(number: $number){
                number
            }
        }
        """

        variables = {
            'number': chat[chat_id]['block']
        }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response.json()

    @staticmethod
    def apartment(chat, chat_id):
        LOGGER.debug("Checking if the informed apartment exists in database")
        query = """
        query apartment($number: String!, $block: String!){
            apartment(number: $number, block: $block){
                number
                block{
                    number
                }
            }
        }
        """

        variables = {
            'number': chat[chat_id]['apartment'],
            'block': chat[chat_id]['block']
        }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response.json()

class CheckResident:

    @staticmethod
    def email(chat, chat_id):
        LOGGER.debug("Checking if the informed email exists in database")
        query = """
        query resident($email: String!){
            resident(email: $email){
                completeName
            }
        }
        """

        variables = {
            'email': chat[chat_id]['email']
        }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response.json()

    @staticmethod
    def cpf(chat, chat_id):
        LOGGER.debug("Checking if the informed CPF exists in database")
        query = """
        query resident($cpf: String!){
            resident(cpf: $cpf){
                completeName
                
            }
        }
        """

        variables = {
                'cpf': chat[chat_id]['cpf']
                }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response.json()


class CheckVisitor:

    def cpf(chat, chat_id):
        LOGGER.debug("Checking if the informed CPF of visitor exists in database")
        query = """
        query visitor($cpf: String!){
            visitor(cpf: $cpf){
                completeName
            }
        }
        """

        variables = {
            'cpf': chat[chat_id]['cpf']
        }

        response = requests.post(PATH, json={'query': query, 'variables':variables})
        LOGGER.debug(f"Response: {response.json()}")

        return response.json()
