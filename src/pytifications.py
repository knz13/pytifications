
import datetime
from typing import List,Callable
import requests
import hashlib
import sys
import asyncio
from dataclasses import dataclass
from threading import Thread
from PIL import Image
import numpy as np
import io

import time


def numpy_to_bytes(arr: np.array) -> bytearray:
    arr_dtype = bytearray(str(arr.dtype), 'utf-8')
    arr_shape = bytearray(','.join([str(a) for a in arr.shape]), 'utf-8')
    sep = bytearray('|', 'utf-8')
    arr_bytes = arr.ravel().tobytes()
    to_return = arr_dtype + sep + arr_shape + sep + arr_bytes
    return to_return

def image_to_byte_array(image: Image.Image) -> str:
  # BytesIO is a fake file stored in memory
    mem_file = io.BytesIO()
    image = image.resize((512,512))
    image.save(mem_file, "PNG", quality=100)
    return list(bytearray(mem_file.getvalue()))

@dataclass
class PytificationButton:
    text: str
    callback: Callable

class PytificationsMessageWithPhoto:
    def __init__(self,message_id = -1,image = None):
        self._image = image
        self._message_id = message_id

    def edit(self,text: str = "",buttons: List[List[PytificationButton]] =[],photo: Image.Image = None): 
        """
        Method to edit this message in Telegram

        if only the buttons are passed, the text will be kept the same

        if no photo is passed, the old one will be kept

        Args:
            text: (:obj:`str`) message to send instead
            buttons: (:obj:`List[List[PytificationButton]]`) a list of rows each with a list of columns in that row to be used to align the buttons
            photo: (:obj:`PIL.Image`) an image if you wish to change it
        Returns:
            :obj:`True` on success and :obj:`False` if no message was sent before
        """

        if not Pytifications._check_login():
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

        request_data = {
            "username":Pytifications._login,
            "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
            "message_id":self._message_id,
            "buttons":requestedButtons,
            "script_id":Pytifications._script_id
        }

        if photo != None:
            request_data['photo'] = image_to_byte_array(photo)
            self._image = photo
        else:
            request_data['photo'] = image_to_byte_array(self._image)

        if text != "":
            request_data["message"] = text
        
        print(f'edited message with id {self._message_id} to "{text}"')        
        requests.patch('https://pytifications.herokuapp.com/edit_message',json=request_data)
        
        return True



class PytificationsMessage:
    def __init__(self,message_id=-1):

        self._message_id = message_id

    def edit(self,text: str = "",buttons: List[List[PytificationButton]] =[]): 
        """
        Method to edit this message in Telegram

        if only the buttons are passed, the text will be kept the same

        Args:
            text: (:obj:`str`) message to send instead
            buttons: (:obj:`List[List[PytificationButton]]`) a list of rows each with a list of columns in that row to be used to align the buttons
        Returns:
            :obj:`True` on success and :obj:`False` if no message was sent before
        """

        if not Pytifications._check_login():
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

        request_data = {
            "username":Pytifications._login,
            "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
            "message_id":self._message_id,
            "buttons":requestedButtons,
            "script_id":Pytifications._script_id
        }

        

        if text != "":
            request_data["message"] = text
        
        
        requests.patch('https://pytifications.herokuapp.com/edit_message',json=request_data)

        return True




class Pytifications:
    _login = None
    _logged_in = False
    _password = None
    _loop = None
    _registered_callbacks = {}
    _last_message_id = 0
    _script_id = 0
    
   
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

        try:
            res = requests.post('https://pytifications.herokuapp.com/initialize_script',json={
                "username":login,
                "password_hash":hashlib.sha256(password.encode('utf-8')).hexdigest(),
                "script_name":sys.argv[0],
                "script_language":'python'
            })
        except Exception as e:
            print(f'Found exception while logging in: {e}')
            return False
        
        Pytifications._login = login
        Pytifications._password = password
        if res.status_code != 200:
            print(f'could not login... reason: {res.text}')
            return False
        else:
            Pytifications._logged_in = True
            Pytifications._script_id = res.text
            print(f'success logging in to pytifications! script id = {Pytifications._script_id}')

        Thread(target=Pytifications._check_if_any_callbacks_to_be_called,daemon=True).start()
        
        return True

    

    def _check_if_any_callbacks_to_be_called():
        while True:
            time.sleep(3)
            if not Pytifications.am_i_logged_in():
                continue
            try:
                res = requests.get('https://pytifications.herokuapp.com/get_callbacks',json={
                    "username":Pytifications._login,
                    "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
                    "script_id":Pytifications._script_id
                })
            except Exception as e:
                print(e)
                continue
            if res.status_code == 200:
                json = res.json()
                for item in json:
                    Pytifications._registered_callbacks[item]["function"](Pytifications._registered_callbacks[item]['args'])

    def send_message(message: str,buttons: List[List[PytificationButton]] = [],photo : Image.Image=None):
        """
        Use this method to send a message to yourself/your group,

        make sure to have called Pytifications.login() before,


        Args:
            message: (:obj:`str`) message to be sent
            buttons: (:obj:`List[List[PytificationButton]]`) a list of rows each with a list of columns in that row to be used to align the buttons
            photo: (:obj:`PIL.Image`) an image if you wish to send it
        Return:
            False if any errors ocurred, :obj:`PytificationsMessage` if photo is not specified and :obj:`PytificationsMessageWithPhoto` if photo is specified
        """
        if not Pytifications._check_login():
            return False

        returnData = PytificationsMessage()

        if photo != None:
            returnData = PytificationsMessageWithPhoto()

        requestedButtons = []
        for row in buttons:
            rowButtons = []
            for column in row:
                Pytifications._registered_callbacks[column.callback.__name__] = {"function":column.callback,"args":returnData}
                rowButtons.append({
                    "callback_name":column.callback.__name__,
                    "text":column.text
                })
            
            requestedButtons.append(rowButtons)

        request_data = {
                "username":Pytifications._login,
                "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
                "message":message,
                "buttons":requestedButtons,
                "script_id":Pytifications._script_id
        }

        if photo != None:
            request_data['photo'] = image_to_byte_array(photo)

        try:
            res = requests.post('https://pytifications.herokuapp.com/send_message',json=request_data)
        except Exception as e:
            print(f"Found error when sending message: {e}")
            return False

        if res.status_code != 200:
            print(f'could not send message. reason: {res.reason}')
            return False

        Pytifications._last_message_id = int(res.text)

        
        returnData._message_id = int(res.text)
        if photo != None:
            print(f'sent message with photo: "{message}"')
            returnData._image = photo
        
        else:
            print(f'sent message: "{message}"')
        return returnData

    def edit_last_message(message:str = "",buttons: List[List[PytificationButton]] = []):
        """
        Use this method to edit the last sent message from this script

        if only the buttons are passed, the text will be kept the same

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
        
        request_data = {
            "username":Pytifications._login,
            "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
            "message_id":Pytifications._last_message_id,
            "buttons":requestedButtons,
            "script_id":Pytifications._script_id
        }

        

        if message != "":
            request_data["message"] = message
        try:
            requests.patch('https://pytifications.herokuapp.com/edit_message',json=request_data)
        except Exception as e:
            print(f'Found exception while editing message: {e}')

            return False

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
    