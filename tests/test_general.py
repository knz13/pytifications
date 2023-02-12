
from pytifications import *

import random
from hashlib import sha256
import pytest

def hash_string(string:str):
    return sha256(string.encode("utf-8")).hexdigest()


def test_wrong_login():
    assert not Pytifications.am_i_logged_in()

    Pytifications.login(hash_string(str(random.random()*random.randint(0,1000))),hash_string(str(random.random()*random.randint(0,1000))))

    assert not Pytifications.am_i_logged_in()

def test_login():

    assert not Pytifications.am_i_logged_in()

    Pytifications.login("TestingUsername","TestingPassword")

    assert Pytifications._login == "TestingUsername"
    assert Pytifications._password == "TestingPassword"
    assert Pytifications.am_i_logged_in()

def test_message():
    
    message = PytificationsMessage(122)

    assert message._message_id == 122
    message.set_message_id(123)

    assert message._message_id == 123

    try:
        message.edit("something")
    except Exception as e:
        assert e

def test_actual_message():

    prior_len = len(alive_messages)
    message = Pytifications.send_message("Hello!",buttons=[[PytificationButton('something',dummy_callback)]])
    assert type(message) == type(PytificationsMessage())
    assert message._message_id != -1
    assert len(alive_messages) > prior_len
    assert Pytifications._last_message_id == message._message_id
    assert "dummy_callback" in Pytifications._registered_callbacks


def dummy_callback():
    pass

def test_buttons_transform():

    buttons = [
        [
        PytificationButton("Hi!",callback=dummy_callback)
        ]
    ]

    buttons,d = buttons_transform(buttons)

    for row in buttons:
        for column in row:
            assert type(column) == type({})
            assert column["text"] == "Hi!"
            assert column["callback_name"] == "dummy_callback"


    







