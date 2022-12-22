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

* Sending images

```
from pytifications import Pytifications
from PIL import Image

#login and etc...

Pytifications.send_message("hi! i have a photo with me :D",photo=Image.open("image_location.png"))

```

* Callbacks

```
#every message can be sent with buttons attached so you can be responsive with your messages

from pytifications import Pytifications,PytificationButton

#login and etc...


#the callbacks receive an instance of the message (PytificationsMessage or PytificationsMessageWithPhoto) that was sent so you can change it if you want

def my_callback_func(message):
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
* Editing messages
```
message = Pytifications.send_message('message sent from Pytifications!')

#you can simply edit the text
message.edit(text="Edited text")

#or add buttons (if only the buttons are passed, the message will be kept the same)!
def some_callback():
    pass

message.edit(buttons=[
    [
        PytificationsButton(
            text="some callback :D",
            callback=some_callback
        )
    ]
])


```


* Edit last message
```
from pytifications import Pytifications

#login and etc...

Pytifications.send_message("hi, i'm not edited!")

#simply edit the last message from anywhere!
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


    
    

