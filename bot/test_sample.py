import pytest
from register import Register
from unittest.mock import MagicMock, patch
from unittest import mock
from checks import CheckCondo
import requests
import json
import logging

@pytest.fixture
def update(update):
    update.message.text = 'Count of Monte Cristo'
    update.effective_message.contact = '1234567'
    return update

@pytest.fixture(autouse=True)
def register(bot_app, update):
    register = Register
    register.index(update, bot_app)
    return register

def test_register_name(bot_app, update, register):
    register.name(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Telefone:' in msg

def test_validation_register_name(bot_app, update, register):
    update.message.text = '@1234nome'
    register.name(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Por favor, digite apenas o seu nome:' in msg

def test_validation_register_name_with_numbers(bot_app, update, register):
    update.message.text = '1234полное имя'
    register.name(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'não digite números no nome' in msg

def test_validation_register_name_with_address_sign(bot_app, update, register):
    update.message.text = 'count@gmail.com'
    register.name(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Neste momento é hora de digitar o seu nome' in msg

def test_register_phone(bot_app, update, register):
    update.message.text = '12345678'
    register.phone(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Email:' in msg

def test_validation_register_phone_with_character(bot_app, update, register):
    update.message.text = '12aasd34b5f678'
    register.phone(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'digite seu telefone corretamente:' in msg

def test_validation_register_phone_with_character(bot_app, update, register):
    update.message.text = '1'*20
    register.phone(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Telefone excedeu tamanho máximo (15)' in msg

def test_validation_register_phone(bot_app, update, register):
    update.message.text = '12345678'
    register.phone(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Email:' in msg

@patch('checks.requests.post', autospec=True)  #mock object during the test
def test_register_email(mock_post, bot_app, update, register):
    mock_post.return_value.json = lambda : {"errors": {"id": "test"}}
    update.message.text = 'exemplo@exemplo.com'
    register.email(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'CPF:' in msg

@patch('checks.requests.post', autospec=True)
def test_register_cpf(mock_post, bot_app, update, register):
    mock_post.return_value.json = lambda : {"errors": {"id": "test"}}
    update.message.text = '259.844.400-08'
    register.cpf(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Bloco:' in msg

@patch('checks.requests.post', autospec=True)
def test_register_condos(mock_post, bot_app, update, register):
    mock_post.return_value.json = lambda : {"data": {"id": "test"}}
    update.message.text = '1'
    register.block(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Apartamento:' in msg
    update.message.text = '101'
    register.apartment(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'agora cadastrar a sua voz!' in msg

def test_start(bot_app, update, register):
    bot_app.call('start', update)
    update.message.reply_text
    assert update.message.reply_text.called == True

@patch('checks.requests.post', autospec=True)  #mock object during the test
def test_check_block(mock_post, update, bot_app):
    register = Register
    mock_post.return_value.status_code = 404
    mock_post.return_value.json = lambda : {"errors": {"id": "test"}}
    register.index(update, bot_app)
    update.message.text = '1'
    register.block(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'digite um bloco existente' in msg
    print(msg)


"""
@patch('checks.requests.post')  #mock object during the test
def test(mock_post, bot_app, update, register):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json = lambda : {"errors": {"id": "test"}}
    register.index(update, bot_app)
    register.name(update, bot_app)
    update.message.text = '12345678'
    register.phone(update, bot_app)
    update.message.text = 'exemplo@exemplo.com'
    register.email(update, bot_app)
    update.message.text = '259.844.400-08'
    register.cpf(update, bot_app)
    update.message.text = '1'
    mock_post.return_value.json = lambda : {"data": {"id": "test"}}
    register.block(update, bot_app)
    update.message.text = '101'
    register.apartment(update, bot_app)
"""
