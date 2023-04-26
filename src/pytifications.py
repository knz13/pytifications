
import datetime
import logging
import random
from traceback import format_exception, format_tb
from typing import List,Callable
import pytz
import requests
import hashlib
import sys
import asyncio
from dataclasses import dataclass
from threading import Lock, Thread,Event
from PIL import Image
import numpy as np
from queue import SimpleQueue
import io
from contextlib import contextmanager
import time
from hashlib import sha256
from secrets import token_hex
from collections import deque
import atexit

def image_to_byte_array(image: Image.Image) -> str:
  # BytesIO is a fake file stored in memory
    mem_file = io.BytesIO()
    image = image.resize((512,512))
    image.save(mem_file, "PNG", quality=100)
    return list(bytearray(mem_file.getvalue()))

def buttons_transform(buttons):
    requestedButtons = []
    actual_buttons = []
    for row in buttons:
        rowButtons = []
        for column in row:
            
            
            column._id = token_hex(6)
            rowButtons.append({
                "button_id":column._id,
                "text":column.text
            })
            actual_buttons.append(column)
            
        requestedButtons.append(rowButtons)
    return requestedButtons,actual_buttons



alive_messages = []

class InternalPytificationsQueuedTask:
    def __init__(self,function,extra_functions: list,args:tuple) -> None:
        self._function = function
        self._extra_functions = extra_functions
        self._args = args

    def evaluate(self):
        self._function(*self._args)
        for queued_task in self._extra_functions:
            queued_task.evaluate()


class PytificationButton:
    def __init__(self,text:str,callback,*extra_args) -> None:
        """
        A class that represents the buttons to be passed in the message requests

        Args:

            text: :obj:`str` the text inside the button

            callback: :obj:`function(message,*args)` the function to be passed as a callback to when the button is pressed. The function receives a message object followed by whatever parameters are passed as an extra to this function
        """
        self.text = text
        self.callback = callback
        self.extra_args = extra_args
        self._id = ""

class PytificationsMessageWithPhoto:
    def __init__(self,message_id,image = None):
        self._image = image

        self._message_id = message_id
        alive_messages.append(self)
    def __del__(self):
        if self in alive_messages:
            alive_messages.remove(self)

    

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
            :obj:`True` if change added to the editing queue and :obj:`False` if an error was found
        """


        if not Pytifications._check_login() or self._message_id == -1:
            return False
        
        
        if isinstance(self._message_id,InternalPytificationsQueuedTask):
            self._message_id._extra_functions.append(InternalPytificationsQueuedTask(self.edit,[],[self,text,buttons,photo]))
            return True

        text = Pytifications._options.format_string(text)
        buttons,buttons_list = buttons_transform(buttons)

        for button in buttons_list:
            Pytifications._registered_callbacks[button._id] = {"function":button.callback,"args":[self,*button.extra_args]}


        request_data = {
            "username":Pytifications._login,
            "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
            "message_id":self._message_id,
            "buttons":buttons,
            "process_id":Pytifications._process_id,
            "user_id":Pytifications._user_id
        }

        if photo != None:
            request_data['photo'] = image_to_byte_array(photo)
            self._image = photo
        else:
            request_data['photo'] = image_to_byte_array(self._image)
        
        if text != "": 
            request_data["message"] = text
        
        Pytifications._add_to_message_pool(edit_message,request_data,self,Pytifications._options)
        
        return True



class PytificationsMessage:
    def __init__(self,message_id):

        self._message_id = message_id
        alive_messages.append(self)
    def __del__(self):
        if self in alive_messages:
            alive_messages.remove(self)

    

    def edit(self,text: str = "",buttons: List[List[PytificationButton]] =[]): 
        """
        Method to edit this message in Telegram

        if only the buttons are passed, the text will be kept the same

        Args:
            text: (:obj:`str`) message to send instead
            buttons: (:obj:`List[List[PytificationButton]]`) a list of rows each with a list of columns in that row to be used to align the buttons
        Returns:
            :obj:`True` if change added to the editing queue and :obj:`False` if an error ocurred
        """


        if not Pytifications._check_login() or self._message_id == -1:
            return False
        
        if isinstance(self._message_id,InternalPytificationsQueuedTask):
            self._message_id._extra_functions.append(InternalPytificationsQueuedTask(self.edit,[],[self,text,buttons]))
            return True

        text = Pytifications._options.format_string(text)
        buttons,buttons_list = buttons_transform(buttons)
        for button in buttons_list:
            Pytifications._registered_callbacks[button._id] = {"function":button.callback,"args":[self,*button.extra_args]}
        

        request_data = {
            "username":Pytifications._login,
            "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
            "message_id":self._message_id,
            "buttons":buttons,
            "process_id":Pytifications._process_id,
            "user_id":Pytifications._user_id
        }

        

        if text != "":
            request_data["message"] = text
        
        
        
        Pytifications._add_to_message_pool(edit_message,request_data,self,Pytifications._options)
        
        return True



class PytificationsRemoteController:
    _instance = None
    def __init__(self,name) -> None:
        pass

    

def update_message_id(old_message_id,new_message_id):
    print(f'updating messages!')

    for i in alive_messages:
        if int(i._message_id) == int(old_message_id):
            i._message_id = (str(new_message_id))

def datetime_diff(diff: datetime.timedelta):
    format = "%H:%M:%S"
    if diff > datetime.timedelta(hours=24):
        format = f'%j {"days" if diff > datetime.timedelta(hours=48) else "day"} %H:%M:%S'
        diff -= datetime.timedelta(hours=24)
    diff = diff + datetime.timedelta(hours=3)
    return datetime.datetime.fromtimestamp(diff.total_seconds()).strftime(format)

class PytificationsOptions:
    _start_time = datetime.datetime.now(pytz.UTC)
    _should_update_in_server = True

    @staticmethod
    @contextmanager
    def with_custom_options(options):
        """
        Helper decorator to keep the options passed to this function while inside the if statement

        More useful internally
        """
        current_options = Pytifications._options
        with PytificationsOptions.no_update_in_server():
            try:
                Pytifications.set_options(options)
                yield
            finally:
                Pytifications.set_options(current_options)
        

    @staticmethod
    @contextmanager
    def no_update_in_server():
        """
        INTERNAL

        Helper decorator to avoid updating the alias of the script when inside the with statement
        """
        try:
            PytificationsOptions._should_update_in_server = False
            yield None
        finally:
            PytificationsOptions._should_update_in_server = True

    @staticmethod
    @contextmanager
    def default_options():
        """
        INTERNAL

        Helper decorator to keep the default options while inside the with statement without sending alias
        """
        current_options = Pytifications._options
        
        with PytificationsOptions.no_update_in_server() as c:
            try:
                Pytifications.set_options(PytificationsOptions(should_send_script_alias=False))
                yield None
            finally:
                Pytifications.set_options(current_options)


    def __init__(self,send_current_time_on_message=False,send_app_run_time_on_message = False,script_alias = "",should_print_sent_messages=False,should_send_script_alias=True) -> None:
        """
        Data class for the options in Pytifications

        Args:
            send_app_run_time_on_message: (:obj:`bool`) whether to send the current app runtime on the bottom of messages sent and edits
            
            send_current_time_on_message: (:obj:`bool`) whether to send the current time on the bottom of messages sent and edited
            
            script_alias: (:obj:`str`) alias to use when sending the message. Any spaces will be replaced with an underscore. Will appear on the top of the messages as "Message sent from __alias_here__:"  and will be used to send commands to your script
        
            should_print_sent_messages: (:obj:`bool`) whether to print to console when a message is sent

            should_send_script_alias: (:obj:`bool`) wether to send the alias of the script at the top of every message
        """
        
        self._send_app_run_time_on_message = send_app_run_time_on_message
        self._script_alias = script_alias.replace(" ","_")
        self._script_alias = token_hex(6) if script_alias == "" else script_alias

        self._send_current_time_on_message = send_current_time_on_message
        self._should_print_sent_messages = should_print_sent_messages
        self._should_send_script_alias = should_send_script_alias
        
    

    def format_string(self,string):
        """
        Formats a string according to the options
        """
        if self._send_app_run_time_on_message or self._send_current_time_on_message:
            string = f'{string}\n'
        if self._send_app_run_time_on_message:
            string = f'{string}\nrun_time:\n{datetime_diff(datetime.datetime.now(pytz.UTC) - PytificationsOptions._start_time)}'
        if self._send_current_time_on_message:
            string = f'{string}\ncurrent_time:\n{(datetime.datetime.now(pytz.UTC) + Pytifications._prefered_timezone).strftime("%H:%M:%S")}'

        if self._should_send_script_alias:
            string = f'Message sent from "{self._script_alias}":\n\n{string}'
        
        return string

def send_message(request_data,photo: Image,return_data: PytificationsMessage | PytificationsMessageWithPhoto,current_options=None):
    """ if len(Pytifications._messages_sent_or_edited_in_last_minute) > 30:
        print(f"In order to preserve our servers, please wait {30} seconds before sending/editing another message")
         """
    if current_options == None:
        current_options = Pytifications._options
        send_message(request_data,photo,return_data,current_options)
        return
    with PytificationsOptions.with_custom_options(current_options):
        try:
            res = requests.post('https://pytifications.herokuapp.com/send_message',json=request_data)
        except Exception as e:
            print(f"Found error when sending message: {e}")
            return False
        

        if res.status_code != 200:
            print(f'could not send message. reason: {res.text}')
            return False

        Pytifications._last_message_id = int(res.text)

        
        return_data._message_id = int(res.text)
        if photo != None:
            if Pytifications._options._should_print_sent_messages:
                print(f'sent message with photo: "{request_data["message"]}"')
            return_data._image = photo

        else:
            if Pytifications._options._should_print_sent_messages:
                print(f'sent message: "{request_data["message"]}"')

def edit_message(request_data,return_data: PytificationsMessage | PytificationsMessageWithPhoto,current_options=None):
    """ if len(Pytifications._messages_sent_or_edited_in_last_minute) > 30:
        print("") """
    
    if current_options == None:
        current_options = Pytifications._options
        edit_message(request_data,return_data,current_options)
        return
    with PytificationsOptions.with_custom_options(current_options):
        try:     
            res = requests.patch('https://pytifications.herokuapp.com/edit_message',json=request_data)

            if res.status_code != 200:
                print(f'could not edit message. reason: {res.text}')
                return False
        except Exception as e:
            print(f'Found exception while editing message: {e}')
            return False

        if Pytifications._options._should_print_sent_messages:
            print(f'edited message with id {return_data._message_id if not isinstance(return_data._message_id,InternalPytificationsQueuedTask) else Pytifications._last_message_id} to "{request_data["message"]}"')   

def send_registered_commands(extras):
    """
    INTERNAL

    used to send the registered commands to the bot
    """
    message = f'The following commands are registered for the script with alias "{Pytifications._options._script_alias}":'

    message += "\n\nDefault commands:"

    #put the default commands here

    for command in Pytifications._default_commands:
        message += f'\n\n -> command: {command}\n      description: {Pytifications._registered_commands[command]["description"]}'

    custom_commands = any(map(lambda x: x not in Pytifications._default_commands,Pytifications._registered_commands.keys()))

    if custom_commands:
        message += "\n\nCustom commands:"

    for command in Pytifications._registered_commands:
        if command in Pytifications._default_commands:
            continue
        message += f'\n\n -> command: {command}\n      description: {Pytifications._registered_commands[command]["description"]}'

    options = Pytifications._options
    custom_options = PytificationsOptions()
    with PytificationsOptions.no_update_in_server():
        Pytifications.set_options(custom_options)
        Pytifications.send_message(message)
        Pytifications.set_options(options)


def send_started_time(extras):
    alias = Pytifications._options._script_alias
    with PytificationsOptions.default_options():
        Pytifications.send_message(f'script/application "{alias}" was started at:\n{(PytificationsOptions._start_time + Pytifications._prefered_timezone).strftime("%d/%m/%Y, %H:%M:%S")}')

class Pytifications:
    _login = None
    _logged_in = False
    _prefered_timezone = datetime.timedelta(hours=0)
    _password = None
    _loop = None
    _registered_callbacks = {
        "__set_message_id":{"function":lambda *args: Pytifications._add_to_message_pool(update_message_id,*args),"args":[]}
    }
    _registered_commands = {
        "check_commands":{"function":send_registered_commands,"description":"shows the available commands for this script/application"},
        "started_time":{"function":send_started_time,"description":"shows the time that the script/application was launched"}
    }
    _default_commands = [
        "check_commands",
        "started_time"
    ]
    _commands_to_call_synchronous = []
    _message_pool: SimpleQueue[InternalPytificationsQueuedTask] = SimpleQueue()
    _last_message_id = 0
    _process_id = 0
    _callbacks_to_call_synchronous = []
    _synchronous = False
    _options = PytificationsOptions()
    _commands_mutex = Lock()
    _callbacks_mutex = Lock()
    _background_thread_event = Event()
    _background_thread = None
    _messages_sent_or_edited_in_last_minute = deque([])
    _traceback_message = ""
    _user_id = 0


    @staticmethod
    def _add_to_message_pool(function,*args):
        """
        INTERNAL
        
        Used to add a function to be run when the message pool is updated

        Used to avoid stopping the application every time a message is sent
        """
        
        task = InternalPytificationsQueuedTask(function,[],args)
        Pytifications._message_pool.put(task)

        return task
    
    @staticmethod
    def add_command_handler(command: str,function,description=""):
        """
        Use this method to add a command handler that can be called from the conversation as !my_script_alias my_command

        The function will receive a string containing any other arguments that were passed in the conversation or an empty string if only the command was passed
        
        Args:
            :obj:`str` the command as a string that will be registered

            :obj:`function(str)` the callback function to be called

            :obj:`str` description of the command (optional)
        """

        Pytifications._registered_commands[command] = {"function":function,"description":description}


        

    @staticmethod
    def run_events_sync():
        """
        Use this method to run all the callbacks/commands that were registered to be called since last time you called this function or started the process
        
        Returns:
            :obj:`True` if any callbacks/commands where called, :obj:`False` otherwise
        """
        
        called_any = False
        if Pytifications._callbacks_mutex.acquire(blocking=False):
            for callback in Pytifications._callbacks_to_call_synchronous:
                called_any = True
                callback["function"](*callback["args"])
            Pytifications._callbacks_to_call_synchronous.clear()
            Pytifications._callbacks_mutex.release()
        if Pytifications._commands_mutex.acquire(blocking=False):
            for command in Pytifications._commands_to_call_synchronous:
                if command["command_name"] not in Pytifications._default_commands:
                    called_any = True
                command["function"](command["args"])
            Pytifications._commands_to_call_synchronous.clear()
            Pytifications._commands_mutex.release()
        
        

        return called_any
    
    @staticmethod
    def set_options(options: PytificationsOptions):
        """
        Sets the options to use during the script operation,

        Make sure to call before the login method to ensure that all options are followed
        
        for more information on the available options check :obj:`PytificationsOptions`
        """
        if Pytifications._logged_in and PytificationsOptions._should_update_in_server and options._script_alias != Pytifications._options._script_alias:
            requests.patch("https://pytifications.herokuapp.com/update_process_name",json={
                "username":Pytifications._login,
                "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
                "process_id":Pytifications._process_id,
                "process_name":options._script_alias,
                "user_id":Pytifications._process_id
            })
        Pytifications._options = options
    
    @staticmethod
    def set_synchronous():
        """
        Use this method to set the callbacks registered in buttons to be called synchronously*
        
        *when you call the function Pytifications.run_callbacks_sync()
        """

        Pytifications._synchronous = True

    @staticmethod
    def set_asynchronous():
        """
        Use this method to set the callbacks registered in buttons to be called asynchronously whenever the process receives the request to call them

        This is the default option
        """
        Pytifications._synchronous = False
    
    @staticmethod
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
                "process_name":Pytifications._options._script_alias,
                "process_language":'python',
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
            json = res.json()
            Pytifications._logged_in = True
            Pytifications._process_id = json['id']
            Pytifications._user_id = json['user_id']
            Pytifications._prefered_timezone = datetime.timedelta(hours=json['prefered_timezone'])

            print(f'success logging in to pytifications! script id = {Pytifications._process_id}')

        sys.excepthook = Pytifications._handle_global_exceptions
        atexit.register(Pytifications._on_script_ended)

        Pytifications._background_thread = Thread(target=Pytifications._check_if_any_events_called,daemon=True,args=(Pytifications._background_thread_event,Pytifications._callbacks_mutex,Pytifications._commands_mutex))
        Pytifications._background_thread.start()
        
        return True
    
    @staticmethod
    def _handle_global_exceptions(e_type, e_value, e_traceback):
        logging.getLogger(__name__).critical("Unhandled exception", exc_info=(e_type, e_value, e_traceback))
        if Pytifications.am_i_logged_in():
            Pytifications._traceback_message = f'An error ocurred in script/application with alias "{Pytifications._options._script_alias}":\n\nError type: {e_type}\n\nError value: {e_value}\n\nTraceback: {"".join(format_tb(e_traceback))}'
            Pytifications._background_thread_event.set()
            while not Pytifications._message_pool.empty():
                try:
                    Pytifications._message_pool.get().evaluate()
                except Exception as e:
                    print(f'Error found while updating message pool, please report to the developer! {e}')
                    pass
            while Pytifications._background_thread.is_alive():
                pass

    @staticmethod
    def _on_script_ended():
        if Pytifications.am_i_logged_in():
            Pytifications._background_thread_event.set()
            while not Pytifications._message_pool.empty():
                try:
                    Pytifications._message_pool.get().evaluate()
                except Exception as e:
                    print(f'Error found while updating message pool, please report to the developer! {e}')
                    pass
            while Pytifications._background_thread.is_alive():
                pass
    
    @staticmethod
    def _check_if_any_events_called(stop_event: Event,callback_lock,command_lock):
        """
        INTERNAL
        
        Used for the inside logic to check if any callbacks or commands to be called
        """
        while True:
            if not Pytifications.am_i_logged_in():
                continue

            while not Pytifications._message_pool.empty():
                try:
                    Pytifications._message_pool.get().evaluate()
                except Exception as e:
                    print(f'Error found while updating message pool, please report to the developer! {e}')
                    pass
            
            if stop_event.is_set():
                requests.post('https://pytifications.herokuapp.com/delete_process',json={
                    "username":Pytifications._login,
                    "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
                    "process_id":Pytifications._process_id,
                    "traceback_message":Pytifications._traceback_message,
                    "user_id":Pytifications._user_id
                })
                break

            time.sleep(1)
            if not Pytifications.am_i_logged_in():
                continue
            if stop_event.is_set():
                requests.post('https://pytifications.herokuapp.com/delete_process',json={
                    "username":Pytifications._login,
                    "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
                    "process_id":Pytifications._process_id,
                    "traceback_message":Pytifications._traceback_message,
                    "user_id":Pytifications._user_id
                })
                break
            
            

            time.sleep(1)
            if stop_event.is_set():
                requests.post('https://pytifications.herokuapp.com/delete_process',json={
                    "username":Pytifications._login,
                    "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
                    "process_id":Pytifications._process_id,
                    "traceback_message":Pytifications._traceback_message,
                    "user_id":Pytifications._user_id
                })
                break
            try:
                res = requests.get('https://pytifications.herokuapp.com/get_callbacks',json={
                    "username":Pytifications._login,
                    "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
                    "process_id":Pytifications._process_id,
                    "user_id":Pytifications._user_id
                })
            except Exception as e:
                print(f'Error found while requesting to get callbacks, please contact the developer! {e}')
                continue
            if res.status_code == 200:
                json = res.json()
                commands,callbacks = json['commands'],json['callbacks']
                for item in callbacks:
                    if Pytifications._synchronous:
                        #print(f'registered_callbacks = {Pytifications._registered_callbacks}')
                        #print(f'got json = {callbacks}')
                        with callback_lock:
                            Pytifications._callbacks_to_call_synchronous.append({
                                "function":Pytifications._registered_callbacks[item["button_id"]]["function"],
                                "args":(Pytifications._registered_callbacks[item['button_id']]['args'] + item["args"])
                            })
                        #print(Pytifications._callbacks_to_call_synchronous)
                    else:
                        Pytifications._registered_callbacks[item["button_id"]]["function"](*(Pytifications._registered_callbacks[item['button_id']]['args'] + item["args"]))
                for item in commands:
                    if item['command'] in Pytifications._registered_commands:
                        if Pytifications._synchronous:
                                with command_lock:
                                    Pytifications._commands_to_call_synchronous.append({
                                        "function":Pytifications._registered_commands[item['command']]["function"],
                                        "args":item['args'],
                                        "command_name":item["command"]
                                    })
                        else:
                            Pytifications._registered_commands[item['command']]["function"](item['args'])
                    else:
                        with PytificationsOptions.default_options():
                            Pytifications.send_message(f'No command was registered with name "{item["command"]}".\n\nAre you sure this is the intended command?')



    @staticmethod
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
        message = Pytifications._options.format_string(message)

        if not Pytifications._check_login():
            return False

        return_data = PytificationsMessage(-1)

        if photo != None:
            return_data = PytificationsMessageWithPhoto(-1)

        buttons,buttons_list = buttons_transform(buttons)
        for button in buttons_list:
            Pytifications._registered_callbacks[button._id] = {"function":button.callback,"args":[return_data,*button.extra_args]}
        

        request_data = {
                "username":Pytifications._login,
                "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
                "message":message,
                "buttons":buttons,
                "process_id":Pytifications._process_id,
                "user_id":Pytifications._user_id
        }

        if photo != None:
            request_data['photo'] = image_to_byte_array(photo)

        task = Pytifications._add_to_message_pool(send_message,request_data,photo,return_data,Pytifications._options)
        return_data._message_id = task

        return return_data

    @staticmethod
    def __edit_last_message(message_return: PytificationsMessage | PytificationsMessageWithPhoto,message:str = "",buttons: List[List[PytificationButton]] = []):
        """
        INTERNAL

        method used to run the message editing in the event pool
        """
        message = Pytifications._options.format_string(message)
        

        buttons,buttons_list = buttons_transform(buttons)
        for button in buttons_list:
            Pytifications._registered_callbacks[button._id] = {"function":button.callback,"args":[message_return,*button.extra_args]}
        
        request_data = {
            "username":Pytifications._login,
            "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
            "message_id":Pytifications._last_message_id,
            "buttons":buttons,
            "process_id":Pytifications._process_id,
            "user_id":Pytifications._user_id
        }

        

        if message != "":
            request_data["message"] = message

        task = Pytifications._add_to_message_pool(edit_message,request_data,message_return,Pytifications._options)
        message_return._message_id = task
        

    @staticmethod
    def edit_last_message(message:str = "",buttons: List[List[PytificationButton]] = []):
        """
        Use this method to edit the last sent message from this script

        if only the buttons are passed, the text will be kept the same

        Args:
            message: (:obj:`str`) message to be sent
            buttons: (:obj:`List[List[PytificationButton]]`) a list of rows each with a list of columns in that row to be used to align the buttons
        Returns:
            :obj:`PytificationsMessage` message object that can be further edited if needed
        """
        if not Pytifications._check_login():
            return False
        
        message_return = PytificationsMessage(-1)
        task = Pytifications._add_to_message_pool(Pytifications.__edit_last_message,message_return,message,buttons)
        message_return._message_id = task
        

        return message_return
        
    @staticmethod
    def _check_login():
        """
        INTERNAL

        Method that checks if already logged in inside this script
        """
        if not Pytifications._logged_in:
            print('could not send pynotification, make sure you have called Pytifications.login("username","password")')
            return False
        return True
    
    
    @staticmethod
    def am_i_logged_in():
        """
        Checks if already logged in
        """
        return Pytifications._logged_in
    
    @staticmethod
    def enable_remote_control(name):
        """
        EXPERIMENTAL: DO NOT USE
        """

        if PytificationsRemoteController._instance == None:
            return PytificationsRemoteController(name)
        else:
            return PytificationsRemoteController._instance
    
