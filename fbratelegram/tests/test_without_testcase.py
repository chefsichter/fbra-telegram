import sys
import threading
import time

from fbratelegram.client import Client
from test_keys import bot_token, chat_id

client = Client(bot_token=bot_token, log_stderr=True)
client.start_loop(blocking=False)
sys.stderr.write("An error was raised")
time.sleep(1)


def err_func():
    time.sleep(1)
    # 5/0
    raise Exception("Stderr ?")


threading.Thread(target=err_func).start()
time.sleep(20)
client.stop_loop()
