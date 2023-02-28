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

    #and send any message you wish!
    Pytifications.send_message("hello from python!")

# Core features

## Options

there are a few options that can be set inside the code (preferably before the login method in order to setup everything) which you can call like this
```
Pytifications.set_options(PytificationsOptions(
    send_app_run_time_on_message=True,
    send_current_time_on_message=True,
    script_alias="my_script"
))
```

the script alias will be used many times so choose the alias wisely :D

## Callbacks

every message can be sent with buttons attached so you can be responsive with your messages
```
from pytifications import Pytifications,PytificationButton

#login and etc...


#the callbacks receive an instance of the message (PytificationsMessage or PytificationsMessageWithPhoto) that was sent so you can change it if you want

def my_callback_func(message):
    print('called!')

    #if you want you can also edit the message
    message.edit("i was changed by a callback :)")

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

# By default the callbacks will be called asynchronously whenever the server receives the signal that the button was pressed, you can override this if you want, like so:

#setting synchronous mode
Pytifications.set_synchronous()

#then just call this method in the main loop of your program when you wish the callbacks to be called
Pytifications.run_events_sync()

```
## Conversational commands

If the buttons don't suit your needs for interactability, you can create commands by calling the following method somewhere in your code (preferably at the start)
```

#creating the callback method, it will receive a string containing any extra arguments passed in the message
def my_callback_function(extra_args):
    #custom code goes here
    print(extra_args)

#then register it
Pytifications.add_command_handler(
        command="my_custom_command",
        function=my_callback_function,
        description="my custom description!"
)
```
Then you can use the chat commands that can be called from the conversation by sending the following message in a chat that the Pytificator bot is in:
```
!my_script_alias my_custom_command [extra_optional_args]
```

To check which commands are available for your script you can use the following command in the chat:
```
!my_script_alias check_commands
```

## Editing messages
every message can be edited after being sent, which you can use to avoid spamming many messages, to update graphs, to update your coworkers instantly and much more!
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

## Edit last message
if you lost the message object you last sent, you can always call the edit_last_message method to edit it!
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

## Sending images

many times it might be useful to send images together with your message (such as sending graphs, script results and such) so we've addressed this need too!

```
from pytifications import Pytifications
from PIL import Image

#login and etc...

Pytifications.send_message("hi! i have a photo with me :D",photo=Image.open("image_location.png"))

```



    
    

