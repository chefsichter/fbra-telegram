# Send a message to your bot.
import time

from fbra_telegram.client import Client
from tests.test_keys import bot_token

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

# Always set the 'telegram.start_loop()' at the end of your code
# or after initialization of all commands.
telegram.start_loop()
time.sleep(5*60)

# stop the loop at the end of your code or if you don't need
# 'telegram commands' anymore. It will need ca. 10 seconds to shutdown.
telegram.stop_loop()
