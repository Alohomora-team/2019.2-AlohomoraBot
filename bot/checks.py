from settings import PATH, LOG_NAME
import os
import requests
import logging

logger = logging.getLogger(LOG_NAME)

class CheckCondo:

    def block(chat, chat_id):
        logger.debug("Checking if the informed block exists in database")
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
        logger.debug(f"Response: {response.json()}")

        return response.json()

    def apartment(chat, chat_id):
        logger.debug("Checking if the informed apartment exists in database")
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
        logger.debug(f"Response: {response.json()}")

        return response.json()

class CheckResident:

    def email(chat, chat_id):
        logger.debug("Checking if the informed email exists in database")
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
        logger.debug(f"Response: {response.json()}")

        return response.json()

    def cpf(chat, chat_id):
        logger.debug("Checking if the informed CPF exists in database")
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
        logger.debug(f"Response: {response.json()}")

        return response.json()


class CheckVisitor: 

    def cpf(chat, chat_id):
        logger.debug("Checking if the informed CPF of visitor exists in database")
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
        logger.debug(f"Response: {response.json()}")

        return response.json()
