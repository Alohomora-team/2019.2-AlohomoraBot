import logging

# API Path
PATH = "http://api:8000/graphql/"

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
VISITOR_REGISTER_NAME, VISITOR_REGISTER_CPF, VERIFY_REGISTRATION, VISITOR_CPF, VISITOR_BLOCK, VISITOR_APARTMENT, CREATE_VISITOR_ENTRY = range(7)

#Handle entry visitors constants
HANDLE_VISITORS_PENDING = range(1)

# Auth constants
CPF_AUTH, VOICE_AUTH = range(2)

# Feedback constants
FEEDBACK = range(1)

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
#TOKEN = "801020772:AAGiaVK52MBf7is4InDnESbB0XE1m9QRcAo"
TOKEN = '916144454:AAHW77nw0ediIcqbryoAK7aW_4TLctfSFkA'

#Log file name
FILE_NAME = 'file.log'
