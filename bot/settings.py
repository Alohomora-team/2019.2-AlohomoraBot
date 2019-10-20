import logging

# API Path
PATH = "http://localhost:8000/graphql/"

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
TOKEN = "862578806:AAG_SMYXi3JGKShYE-lmfqyl6Xrc6JmxJ1s"

#Log file name
FILE_NAME = 'file.log'
