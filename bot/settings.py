import logging

# API Path
PATH = "http://api:8000/graphql/"

# Register constants
NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, VOICE_REGISTER, REPEAT_VOICE = range(8)

# Auth constants
CPF_AUTH, VOICE_AUTH = range(2)

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
TOKEN = "724918697:AAF_CYQtfDtbrr8YpHU3K6RKvLJQXRJiHWY"

#Log file name
FILE_NAME = 'file.log'
