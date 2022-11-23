# Pytifications

This is a python package to send messages to your telegram from python code

# Installation

We are on PyPi! just paste this code on terminal

    pip install pytifications

And you're done

# Usage

First you'll need to create an account at the [pytificator](https://t.me/pytificator_bot) bot

After that just import the library like so
    
    from pytifications import Pytifications


    #use your credentials created at the bot
    Pytifications.login("myUsername","myPassword")

    #and send!
    Pytifications.send_message("hello from python!")
    

## Extra features

* Callbacks

```
#every message can be sent with buttons attached so you can be responsive with your messages

from pytifications import Pytifications,PytificationButton

#login and etc...

def my_callback_func():
    print('called!')

Pytifications.send_message('hi!',buttons=[
    #each column is an inner list
    [
        #use the PytificationButton
        PytificationButton(
            text="I'm a button!",
            callback=my_callback_func
        )
    ]
])
```
* Edit last message
```
from pytifications import Pytifications

#login and etc...

Pytifications.send_message("hi, i'm not edited!")

#simply edit the last message
Pytifications.edit_last_message("now i am!")

#you can also change the buttons on the message!

def do_something():
    print('something done!')

Pytifications.edit_last_message("now with buttons!",buttons=[
    [
        PytificationButton(
            text="do something...",
            callback=do_something
        )
    ]
])
```


    
    

