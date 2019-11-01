import pytest
from unittest.mock import MagicMock, patch
from unittest import mock
from checks import CheckCondo
import requests
import json
import logging

@pytest.fixture
def update(update, tg_voice_size):
    update.message.text = 'Count of Monte Cristo'
    update.effective_message.contact = '1234567'
    return update

@pytest.fixture
def response(read_fixture):
    return read_fixture('checkUser')

@pytest.mark.parametrize('input, output', [
    ['Count of Monte Cristo', 'Telefone:'],
    ['@1234nome', 'Por favor, digite apenas o seu nome:'],
    ['1234msdmsd asd', 'não digite números no nome'],
    ['count@gmail.com', 'Neste momento é hora de digitar o seu nome'],
])
def test_register_name(input, output, bot_app, update, register):
    update.message.text = input
    register.name(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert output in msg

@pytest.mark.parametrize('input, output', [
    ['12345678', 'Email:'],
    ['12aasd34b5f678', 'digite seu telefone corretamente:'],
    ['1'*20, 'Telefone excedeu tamanho máximo (15)'],
    ['12345678', 'Email:'],
])
def test_validation_register_phone(input, output, bot_app, update, register):
    update.message.text = input
    register.phone(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert output in msg

"""
def test_start(bot_app, update):
    bot_app.call('start', update)
    assert update.message.reply_text.called == True
"""

@pytest.mark.parametrize('input, output', [
    ['exemplo@exemplo.com', 'CPF:'],
    ['exemplo com', 'Por favor, digite um email válido:'],
    ['@.'*200, 'Email excedeu tamanho máximo (90), tente novamente:'],
])

@patch('checks.requests.post', autospec=True)  #mock object during the test
def test_register_email(mock_post, bot_app, update, register, input, output):
    mock_post.return_value.json = lambda : {"errors": {"id": "test"}}
    update.message.text = input
    register.email(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert output in msg

@patch('checks.requests.post', autospec=True)
def test_register_cpf(mock_post, bot_app, update, register):
    mock_post.return_value.json = lambda : {"errors": {"id": "test"}}
    update.message.text = '259.844.400-08'
    register.cpf(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Bloco:' in msg

"""
def test_validation_register_cpf_wrong(bot_app, update, register):
    update.message.text = '12345678910'
    register.cpf(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Por favor, digite o CPF com os 11 digitos: (Ex: 123.456.789-10)' in msg
"""

@pytest.mark.parametrize('input, output', [
    ['1', 'Apartamento:'],
    ['101asd ', 'Por favor, digite apenas o bloco: (Ex: 1)'],
    ['1'*10, 'Digte um bloco de até 4 caracteres:'],
])

@patch('checks.requests.post', autospec=True)
def test_register_block(mock_post, bot_app, update, register, input, output):
    mock_post.return_value.json = lambda : {"data": {"id": "test"}}
    update.message.text = input
    register.block(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert output in msg

@pytest.mark.parametrize('input, output', [
    ['101', 'agora cadastrar a sua voz!'],
    ['asdasd ', 'Por favor, digite apenas o apartamento: (Ex: 101)'],
    ['1'*10, 'Digite um apartamente de até 6 caracteres:'],
])

@patch('checks.requests.post', autospec=True)
def test_register_apartment(mock_post, bot_app, update, register, input, output):
    mock_post.return_value.json = lambda : {"data": {"id": "test"}}
    update.message.text = '1'
    register.block(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    update.message.text = input
    register.apartment(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert output in msg

@patch('checks.requests.post', autospec=True)  #mock object during the test
def test_check_block(mock_post, update, bot_app, register):
    mock_post.return_value.status_code = 404
    mock_post.return_value.json = lambda : {"errors": {"id": "test"}}
    register.index(update, bot_app)
    update.message.text = '1'
    register.block(update, bot_app)
    msg = update.message.reply_text.call_args[1]['text']
    assert 'digite um bloco existente' in msg

def test_validation_voice_long_duration(bot_app, update, register):
    update.message.voice.duration = 3
    register.voice_register(update, bot_app);
    msg = update.message.reply_text.call_args[1]['text']
    assert 'grave novamente' in msg

def test_validation_voice_short_duration(bot_app, update, register):
    update.message.voice.duration = 0.9
    register.voice_register(update, bot_app);
    msg = update.message.reply_text.call_args[1]['text']
    assert 'grave novamente' in msg

def test_end(bot_app, update, register):
    register.end(update, bot_app);
    msg = update.message.reply_text.call_args[1]['text']
    assert 'Cadastro cancelado!' in msg

"""
@patch('checks.requests.post')  #mock object during the test
def test(mock_post, bot_app, update, register, response):
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
    mock_post.return_value.json = response
    chat_id = update.message.chat_id
    register.register_user(update.message.chat_id)
"""
