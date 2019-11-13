"""
Provides functionalities to admins
"""
from settings import PATH
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

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        return response.json()

    def delete_resident(email):
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

        response = requests.post(PATH, json={'query':query, 'variables':variables})

        return response.json()
