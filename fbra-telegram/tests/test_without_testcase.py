import sys
import threading
import time
from client import TelegramClient
from test_keys import bot_token, chat_id

client = TelegramClient(bot_token=bot_token, chat_id=chat_id, log_stderr=True)
client.start_loop()
sys.stderr.write("An error was raised")
time.sleep(1)


def err_func():
    time.sleep(1)
    5/0
    raise Exception("Stderr ?")


threading.Thread(target=err_func).start()
time.sleep(2)
client.stop_loop()
