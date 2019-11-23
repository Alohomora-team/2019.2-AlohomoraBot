"""
Constants used in all code
"""
import os
import logging

# API Path
PATH = os.environ.get('URL_PATH', "http://api:8000/graphql/")

# Register constants
NAME = 0
PHONE = 1
EMAIL = 2
CPF = 3
BLOCK = 4
APARTMENT = 5
PASSWORD = 6
CATCH_AUDIO_SPEAKING_NAME = 7
CONFIRM_AUDIO_SPEAKING_NAME = 8
VOICE_REGISTER = 9
REPEAT_VOICE = 10

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
CHOOSE_AUTH, SHOW_VISITORS, CPF_AUTH, VOICE_AUTH, PASSWORD_AUTH = range(5)

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
TOKEN = os.environ.get('TOKEN', "801020772:AAGiaVK52MBf7is4InDnESbB0XE1m9QRcAo")

#Log file name
FILE_NAME = 'file.log'
