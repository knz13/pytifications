
import requests
import hashlib
import sys


class Pytifications:
    _login = None
    _logged_in = False
    _password = None
    def login(login,password):
        Pytifications._logged_in = False

        res = requests.post('https://pytifications.herokuapp.com/send_message',{
            "username":login,
            "password_hash":hashlib.sha256(password.encode('utf-8')).hexdigest(),
            "message":""
        })
        Pytifications._login = login
        Pytifications._password = password
        if res.status_code != 200:
            print(res.reason)
        else:
            Pytifications._logged_in = True
            print('success logging in to pytifications!')
    

    def send_message(message: str):
        if not Pytifications._logged_in:
            print('could not send pynotification, make sure you have called Pytifications.login("username","password")')
            return
        
        requests.post('https://pytifications.herokuapp.com/send_message',{
            "username":Pytifications._login,
            "password_hash":hashlib.sha256(Pytifications._password.encode('utf-8')).hexdigest(),
            "message":f'Message sent from {sys.argv[0]}...\n{message}'
        })
        print(f'sent message: "{message}"')

    def am_i_logged_in():
        return Pytifications._logged_in
    