# Send a message to your bot.
import time

from fbratelegram.client import Client
from fbratelegram.tests.test_keys import bot_token

# type '/start' in bot chat window immediately before initializing this python code.
# After initialization the chat_id gets stored in the config.ini file
telegram = Client(bot_token=bot_token)

telegram.send_msg("Hello world.")

def foo():
    print("Hello there.")

def important():
    telegram.send_msg("You wanted to run this function.")

def command_with_args(update, context):
    try:
        arg = context.args[0]
    except IndexError:
        arg = 'crazy'
    telegram.double_log_msg(f"This is {arg} stuff my friend.")

    telegram.add_command("what", command_with_args)

# Add a command to your bot.
telegram.add_command("hello", foo)
# Add a confirmation command to your bot.
telegram.add_confirmation_command("important", important)
# Retrieve arguments from command, e.g. type '/what stuff'
telegram.add_command("what", command_with_args)

# Always set the start_loop(blocking=True) at the end of
# your code. You need it, that the commands work.
telegram.start_loop(blocking=True)

# If blocking is set to False, the telegram loop works
# as long as the main thread is alive.
# telegram.start_loop(blocking=False)
# <Your code>
# If you don't need commmands anymore, you can stop the loop
# telegram.stop_loop()
