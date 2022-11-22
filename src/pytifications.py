
import requests
import hashlib
import sys


class Pytifications:
    def __init__(self,login,password):
        self._logged_in = False

        res = requests.post('https://pytifications.herokuapp.com/send_message',{
            "username":login,
            "password_hash":hashlib.sha256(password.encode('utf-8')).hexdigest(),
            "message":""
        })
        self._login = login
        self._password = password
        if res.status_code != 200:
            print(res.reason)
        else:
            self._logged_in = True
            print('success logging in to pytifications!')

    def send_message(self,message: str):
        if not self._logged_in:
            print('could not send pynotification, make sure you have logged in correctly')
            return    
        
        requests.post('https://pytifications.herokuapp.com/send_message',{
            "username":self._login,
            "password_hash":hashlib.sha256(self._password.encode('utf-8')).hexdigest(),
            "message":f'Message sent from {sys.argv[0]}...\n{message}'
        })
        print(f'sent message: "{message}"')

    def am_i_logged_in(self):
        return self._logged_in
    