"""

import os
import time
import traceback

from tgintegration import BotIntegrationClient
from tgintegration.response import Response
from typing import Dict
import unittest
class TestSum(unittest.TestCase):

    client = BotIntegrationClient(
        bot_under_test='@AlohomoraTestBot',
        session_name='higton',  # Arbitrary file path to the Pyrogram session file
        api_id='1069048',  # See "Requirements" above, ...
        api_hash='98b58c00983cc0e78a0de7285b7a3e36',  # alternatively use a `config.ini` file
        max_wait_response=15,  # Maximum timeout for bot responses
        min_wait_consecutive=2  # Minimum time to wait for consecutive messages
    )
    client.load_config()
    client.start()
    client.clear_chat()  # Let's start with a blank screen
    response = client.send_command_await("start", num_expected=3)
    print("oiiiiiiiiii")
    print(response.num_messages)
    assert response.num_messages == 3
    response = client.send_command_await("cadastrar", num_expected=3)
    print("oiiiiiiiiii")
    print(response.num_messages)
    assert response.num_messages == 3
    res = client.send_message_await("rick", max_wait=2, raise_=False)
    res = client.send_message_await("424242", max_wait=2, raise_=False)
    res = client.send_message_await("email@exemplo.com", max_wait=2, raise_=False)
    res = client.send_message_await("542.452.606-37", max_wait=2, raise_=False)
    res = client.send_message_await("1", max_wait=2, raise_=False)
    res = client.send_message_await("101", max_wait=2, raise_=False)

    response = client.send_command_await("cancelar", num_expected=1)
    print("oiiiiiiiiii")
    print(response.num_messages)
    assert response.num_messages == 1
    client.stop()

if __name__ == "__main__":
    unittest.main()
"""
