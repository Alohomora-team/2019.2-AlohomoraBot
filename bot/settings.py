import logging

# API Path
PATH = "http://localhost:8000/graphql/"

# Register constants
NAME, PHONE, EMAIL, CPF, BLOCK, APARTMENT, VOICE_REGISTER, REPEAT_VOICE = range(8)

# Auth constants
CPF_AUTH, VOICE_AUTH = range(2)

# Log format
FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

# Log date format
DATEFMT = '%d/%m/%Y %I:%M:%S'

# Log level
LEVEL = logging.DEBUG

# Bot token
TOKEN = "862578806:AAG_SMYXi3JGKShYE-lmfqyl6Xrc6JmxJ1s"
