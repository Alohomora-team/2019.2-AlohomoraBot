"""
Check information about condominium
"""

import logging
import os
import requests

from settings import PATH, LOG_NAME, API_TOKEN

logger = logging.getLogger(LOG_NAME)

class CheckCondo:
    """
    Check information about blocks and apartments
    """

    def block(block):
        """
        Check block information
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
                'number': block
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(
                PATH,
                headers=headers,
                json={'query': query, 'variables':variables}
                )
        logger.debug(f"Response: {response.json()}")

        return response.json()

    def apartment(block, apartment):
        """
        Check apartment information
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
                'number': apartment,
                'block': block
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(
                PATH,
                headers=headers,
                json={'query': query, 'variables':variables}
                )
        logger.debug(f"Response: {response.json()}")

        return response.json()

class CheckResident:
    """
    Check resident information
    """

    def email(email):
        """
        Check email information
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
                'email': email
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(
                PATH,
                headers=headers,
                json={'query': query, 'variables':variables}
                )
        logger.debug(f"Response: {response.json()}")

        return response.json()

    def cpf(cpf):
        """
        Check cpf information
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
                'cpf': cpf
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(
                PATH,
                headers=headers,
                json={'query': query, 'variables':variables}
                )
        logger.debug(f"Response: {response.json()}")

        return response.json()


class CheckVisitor:
    """
    check visitor data
    """

    def cpf(cpf):
        """
        Check if cpf is valid
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
                'cpf': cpf
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(
                PATH,
                headers=headers,
                json={'query': query, 'variables':variables}
                )
        logger.debug(f"Response: {response.json()}")

        return response.json()

class CheckAdmin:
    """
    Check admin information
    """

    def email(email):
        """
        Check if admin email exists in database
        """

        logger.debug("Checking if the informed email exists in database")
        query = """
        query admin($adminEmail: String!){
            admin(adminEmail: $adminEmail){
                admin {
                    email
                }
            }
        }
        """

        variables = {
                'adminEmail': email
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(
                PATH,
                headers=headers,
                json={'query': query, 'variables':variables}
                )
        logger.debug(f"Response: {response.json()}")

        return response.json()
