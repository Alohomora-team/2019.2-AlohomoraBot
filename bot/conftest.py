import pytest
from register import Register
from unittest.mock import MagicMock, patch
from faker import Faker
import base64
faker = Faker()
from random import randint
from os import path
import json

def factory(class_name: str = None, **kwargs):
    """Simple factory to create a class with attributes from kwargs"""
    class FactoryGeneratedClass:
        pass

    rewrite = {
        '__randint': lambda *args: randint(100_000_000, 999_999_999),
    }

    for key, value in kwargs.items():
        if value in rewrite:
            value = rewrite[value](value)

        setattr(FactoryGeneratedClass, key, value)

    if class_name is not None:
        FactoryGeneratedClass.__qualname__ = class_name
        FactoryGeneratedClass.__name__ = class_name

    return FactoryGeneratedClass
@pytest.fixture
def message(tg_voice_size):
    """telegram.Message"""
    return lambda **kwargs: factory(
        'Message',
        chat_id='1',
        voice = tg_voice_size(),
        reply_text=MagicMock(return_value=factory(message_id=100800)()),  # always 100800 as the replied message id
        **kwargs,

    )()

@pytest.fixture
def bot(message):
    """Mocked instance of the bot"""
    class Bot:
        send_message = MagicMock()

    return Bot()

@pytest.fixture
def bot_app(bot):
    """Our bot app, adds the magic curring `call` method to call it with fake bot"""
    import main  #main.py
    setattr(main, 'call', lambda method, *args, **kwargs: getattr(main, method)(bot, *args, **kwargs))
    return main

@pytest.fixture
def update(message):
    """telegram.Update"""
    return factory(
        'Update',
        update_id='__randint',
        message=message(),
        effective_message=message(),
    )()

@pytest.fixture
def register(bot_app, update):
    register = Register
    register.index(update, bot_app)
    return register

@pytest.fixture
def tg_voice_file():
    """telegram.File"""

    return lambda **kwargs: factory(
        'File',
        file_id='__randint',
        file_size=None,
        duration=0.5,
        file_path='/tmp/path/to/file.png',
        download=MagicMock(),
        **kwargs,
    )()


@pytest.fixture
def tg_voice_size(tg_voice_file):
    """telegram.PhotoSize"""
    return lambda **kwargs: factory(
        'VoiceSize',
        file_id='__randint',
        duration=1,
        get_file=MagicMock(tg_voice_file),
        split=MagicMock(),
        **kwargs,
    )()

@pytest.fixture
def read_fixture():
    """Fixture reader"""
    def read_file(f):
        with open(path.join('tests/fixtures/', f) + '.json') as fp:
            return json.load(fp)

    return read_file
