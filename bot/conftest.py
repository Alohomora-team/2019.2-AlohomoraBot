import pytest
from register import Register
from unittest.mock import MagicMock, patch
from faker import Faker
import base64
faker = Faker()
from random import randint

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
def message():
    """telegram.Message"""
    return lambda **kwargs: factory(
        'Message',
        chat_id='1',
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
