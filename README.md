# Pytifications

This is a python package to send messages to your telegram from python code

# Usage

First you'll need to create an account at the [pytificator](t.me/pytificator_bot) bot

After that just import the library like so

    from pytifications import Pytifications


    #use your credentials created at the bot
    Pytifications.login("myUsername","myPassword")

    #and send!
    Pytifications.send_message("hello from python!")