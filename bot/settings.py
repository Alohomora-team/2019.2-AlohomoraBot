import logging

# API Path
PATH = "http://localhost:8000/graphql/"

# Register constants
NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, VOICE_REGISTER, REPEAT_VOICE = range(8)

#Visitor constants
VISITOR_REGISTER_NAME, VISITOR_REGISTER_CPF, VERIFY_REGISTRATION, VISITOR_CPF, VISITOR_BLOCK, VISITOR_APARTMENT, CREATE_VISITOR_ENTRY = range(7)

#Handle entry visitors constants
SHOW_VISITORS_PENDING = range(1)

# Auth constants
CPF_AUTH, VOICE_AUTH = range(2)

# Feedback constants
FEEDBACK = range(1)

# Auth admin and new admin constants
EMAIL_AUTH_ADMIN, PASSWORD_AUTH_ADMIN, REPEAT_AUTH_ADMIN, ADMIN_REGISTER_EMAIL, ADMIN_REGISTER_PASSWORD = range(5)

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
TOKEN = "801020772:AAGiaVK52MBf7is4InDnESbB0XE1m9QRcAo"

#Log file name
FILE_NAME = 'file.log'
