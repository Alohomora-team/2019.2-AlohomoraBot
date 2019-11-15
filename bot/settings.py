"""
Constants used in all code
"""
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

# Resident auth constants
CPF_AUTH, VOICE_AUTH = range(2)

# Visitor register constants
VISITOR_REGISTER_NAME, VISITOR_REGISTER_CPF = range(2)

# Visit constants
VISIT_BLOCK, VISIT_APARTMENT = range(2)

# Admin auth constants
ADMIN_AUTH_EMAIL, ADMIN_AUTH_PWD, ADMIN_AUTH_REPEAT = range(3)

# Admin register constants
ADMIN_REGISTER_EMAIL, ADMIN_REGISTER_PWD = range(2)

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
TOKEN = "724918697:AAF_CYQtfDtbrr8YpHU3K6RKvLJQXRJiHWY"

#Log file name
FILE_NAME = 'file.log'
