import logging

# API Path
PATH = "http://localhost:8000/graphql/"

# Register constants
NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, VOICE_REGISTER, REPEAT_VOICE = range(8)

#Visitor constants
VERIFY_REGISTRATION, VISITOR_CPF, VISITOR_BLOCK = range(3)

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

#Log name
LOG_NAME = 'Alohomora'

# Bot token
TOKEN = "801020772:AAGiaVK52MBf7is4InDnESbB0XE1m9QRcAo"

#Log file name
FILE_NAME = 'file.log'
