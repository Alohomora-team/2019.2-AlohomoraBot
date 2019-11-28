"""
Provides functionalities to admins
"""

from db.schema import get_admin_token
from settings import PATH, API_TOKEN
import requests

class Admin:
    """Provides functionalities to admins"""
    def activate_resident(email):
        """Activate a resident in database"""
        query = """
        mutation activateUser($email: String!){
            activateUser(userEmail: $email){
                user{
                    email
                }
            }
        }
        """

        variables = {
                'email': email
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(PATH, headers=headers, json={'query':query, 'variables':variables})

        return response.json()

    def delete_resident(email, chat_id):
        """Delete a resident in database"""
        query = """
        mutation deleteResident($email: String!){
            deleteResident(residentEmail: $email){
                residentEmail
            }
        }
        """

        variables = {
                'email': email
                }

        headers = {
                'Authorization': 'JWT %s' % get_admin_token(chat_id)
                }

        response = requests.post(PATH, headers=headers, json={'query':query, 'variables':variables})

        return response.json()

    def deactivate_resident(email):
        """Deactivate a resident in database"""
        query = """
        mutation deactivateUser($email: String!){
            deactivateUser(userEmail: $email){
                user{
                    email
                }
            }
        }
        """

        variables = {
                'email': email
                }

        headers = {
                'Authorization': 'JWT %s' % API_TOKEN
                }

        response = requests.post(PATH, headers=headers, json={'query':query, 'variables':variables})

        return response.json()
