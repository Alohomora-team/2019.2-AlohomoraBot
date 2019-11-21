"""
Constants used in all code
"""
import logging

# API Path
PATH = "https://alohomora-hmg.herokuapp.com/graphql/"

# Register constants
NAME = 0
PHONE = 1
EMAIL = 2
CPF = 3
BLOCK = 4
APARTMENT = 5
CATCH_AUDIO_SPEAKING_NAME = 6
CONFIRM_AUDIO_SPEAKING_NAME = 7
VOICE_REGISTER = 8
REPEAT_VOICE = 9

#Visitor constants
VISITOR_REGISTER_NAME = 0
VISITOR_REGISTER_CPF = 1
VERIFY_REGISTRATION = 2
VISITOR_CPF = 3
VISITOR_BLOCK = 4
VISITOR_APARTMENT = 5
CREATE_VISITOR_ENTRY = 6

#Handle entry visitors constants
HANDLE_VISITORS_PENDING = range(1)

# Auth constants
CPF_AUTH, VOICE_AUTH = range(2)

# Feedback constants
FEEDBACK = range(1)

# Auth admin
EMAIL_AUTH_ADMIN, PASSWORD_AUTH_ADMIN, REPEAT_AUTH_ADMIN = range(3)

# New admin constants
ADMIN_REGISTER_EMAIL, ADMIN_REGISTER_PWD = range(2)

# Log format
FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

# Log date format
DATEFMT = '%d/%m/%Y %I:%M:%S'

# Log level
LOG_LEVEL = logging.DEBUG

# API Log level
API_LOG_LEVEL = logging.CRITICAL

#Log name
LOG_NAME = 'Alohomora'

# Bot token
TOKEN = "977525533:AAHvz6R1F_RcUpdv4FfuJ0kcr0_ly4cP8uo"

#Log file name
FILE_NAME = 'file.log'
