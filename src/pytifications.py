
from typing import List,Callable
import requests
import hashlib
import sys
import asyncio
from dataclasses import dataclass
from threading import Thread

import time

@dataclass
class PytificationButton:
    text: str
    callback: Callable



class Pytifications:
    _login = None
    _logged_in = False
    _password = None
    _loop = None
    _registered_callbacks = {}
    _last_message_id = 0


    def login(login:str,password:str) -> bool:
        """
        Use this method to login to the pytifications network,

        if you don't have a login yet, go to https://t.me/pytificator_bot and talk to the bot to create your account

        Args:
            login (:obj:`str`) your login credentials created at the bot
            password (:obj:`str`) your password created at the bot

        Returns:
            :obj:`True`if login was successful else :obj:`False`
        """

        Pytifications._logged_in = False

        res = requests.post('https://pytifications.herokuapp.com/initialize_script',{
            "username":login,
            "password_hash":hashlib.sha256(password.encode('utf-8')).hexdigest(),
            "script_name":sys.argv[0]
        })
        
        Pytifications._login = login
        Pytifications._password = password
        if res.status_code != 200:
            print(f'could not login... reason: {res.text}')
            return False
        else:
            Pytifications._logged_in = True
            print('success logging in to pytifications!')

        Thread(target=Pytifications._check_if_any_callbacks_to_be_called,daemon=True).start()
        
        return True

    def _check_if_any_callbacks_to_be_called():
        while True:
            time.sleep(1)
            if not Pytifications.am_i_logged_in():
                continue
            try:
                res = requests.get('https://pytifications.herokuapp.com/get_callbacks',data={
                    "username":Pytifications._login,
                    "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
                    "script_name":sys.argv[0]
                })
            except:
                pass
            if res.status_code == 200:
                json = res.json()
                for item in json:
                    Pytifications._registered_callbacks[item]()

    def send_message(message: str,buttons: List[List[PytificationButton]] = []):
        """
        Use this method to send a message to yourself/your group,

        make sure to have called Pytifications.login() before,


        Args:
            message: (:obj:`str`) message to be sent
            buttons: (:obj:`List[List[PytificationButton]]`) a list of rows each with a list of columns in that row to be used to align the buttons
        """
        if not Pytifications._check_login():
            return

        requestedButtons = []
        for row in buttons:
            rowButtons = []
            for column in row:
                Pytifications._registered_callbacks[column.callback.__name__] = column.callback
                rowButtons.append({
                    "callback_name":column.callback.__name__,
                    "text":column.text
                })
             
            requestedButtons.append(rowButtons)
        res = requests.post('https://pytifications.herokuapp.com/send_message',{
            "username":Pytifications._login,
            "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
            "message":f'Message sent from {sys.argv[0]}...\n\n{message}',
            "buttons":requestedButtons
        })

        Pytifications._last_message_id = res.json()

        print(f'sent message: "{message}"')

    def edit_last_message(message:str,buttons: List[List[PytificationButton]] = []):
        """
        Use this method to edit the last sent message from this script

        Args:
            message: (:obj:`str`) message to be sent
            buttons: (:obj:`List[List[PytificationButton]]`) a list of rows each with a list of columns in that row to be used to align the buttons
        Returns:
            :obj:`True` on success and :obj:`False` if no message was sent before
        """
        if not Pytifications._check_login() or Pytifications._last_message_id == None:
            return False

        requestedButtons = []
        for row in buttons:
            rowButtons = []
            for column in row:
                Pytifications._registered_callbacks[column.callback.__name__] = column.callback
                rowButtons.append({
                    "callback_name":column.callback.__name__,
                    "text":column.text
                })
             
            requestedButtons.append(rowButtons)
        
        requests.patch('https://pytifications.herokuapp.com/edit_message',data={
            "username":Pytifications._login,
            "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
            "message":message,
            "message_id":Pytifications._last_message_id,
            "buttons":requestedButtons
        })

        return True
        

    def _check_login():
        if not Pytifications._logged_in:
            print('could not send pynotification, make sure you have called Pytifications.login("username","password")')
            return False
        return True


    def am_i_logged_in():
        """
        Checks if already logged in
        """
        return Pytifications._logged_in
    