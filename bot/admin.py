from settings import PATH
import requests

class Admin:

    def activate_resident(email):
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
