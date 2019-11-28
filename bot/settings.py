"""
Constants used in all code
"""

import os
import logging

# API Path
PATH = os.environ.get('URL_PATH', "http://api:8000/graphql/")

# Reisdent register constants
(NAME,
PHONE,
EMAIL,
CPF,
BLOCK,
APARTMENT,
PASSWORD,
VOICE_REGISTER,
REPEAT_VOICE) = range(9)

# Resident auth constants
CHOOSE_AUTH, VOICE_AUTH, PASSWORD_AUTH = range(3)

# Visitor register constants
VISITOR_REGISTER_NAME, VISITOR_REGISTER_CPF = range(2)

# Visit constants
VISIT_BLOCK, VISIT_APARTMENT = range(2)

# Admin register constants
ADMIN_REGISTER_EMAIL, ADMIN_REGISTER_PWD = range(2)

# Admin auth constants
ADMIN_AUTH_EMAIL, ADMIN_AUTH_PWD, ADMIN_AUTH_REPEAT = range(3)

# Feedback constants
FEEDBACK = 0

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

# Bot API token
API_TOKEN = ""

#Log file name
FILE_NAME = 'file.log'
