"""
Check if visitors information is registeredi in database
"""
import logging

from settings import PATH, LOG_NAME

logger = logging.getLogger(LOG_NAME)

class CheckCondo:
    """
    Check informations about condominium
    """

    def block(chat, chat_id):
        """
        Check if block exists
        """
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
        """
        Check if apartments exists in API database
        """
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
    """
    Check resident informations
    """

    def email(chat, chat_id):
        """
        Check if API has that e-mail registered
        """

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
        """
        Checking if cpf exists
        """

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
    """
    Check visitors informations
    """

    def cpf(chat, chat_id):
        """
        Check if visitor have cpf registered
        """

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
