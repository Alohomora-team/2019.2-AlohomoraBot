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
#TOKEN = "724918697:AAF_CYQtfDtbrr8YpHU3K6RKvLJQXRJiHWY"
TOKEN="429283202:AAFAwrd459W0eA7xhgctjsEHOQI4Wl5IjVY"

#Log file name
FILE_NAME = 'file.log'
