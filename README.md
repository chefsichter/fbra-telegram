## Introduction
Send messages and commands to your telegram bot.

fbra-telegram is a wrapper around the 'https://github.com/python-telegram-bot/python-telegram-bot' asyncio package. You can use it like pushbullet.

## Installation
1. You need python >= 3.10.
2. Install telegram desktop client (https://desktop.telegram.org/).
3. Obtain a bot token (https://core.telegram.org/bots/tutorial).

    >Obtaining a token is as simple as contacting <a href="https://t.me/botfather">@BotFather</a>, issuing the **/newbot** command and following the steps until you're given a new token.

    >Your token will look something like this:
4839574812:AAFD39kkdpWt3ywyRZergyOLMaJhac60qc

3. Install fbra-telegram.
    ```
    pip install fbra-telegram
    ```
   
## QuickStart

```python
# This example code is under examples/quick_start.py
# Send a message to your bot.
import time
from fbratelegram.client import Client
```
   > type `/start` in telegram chat bot window `immediately before initializing Client(...) code`.
   
```python
# After initialization of the Client() the chat_id gets stored in the config.ini file
telegram = Client(bot_token=<TELEGRAM-TOKEN>)

telegram.send_msg("Hello world.")
```

```python
# Add a command to your bot.
...
def foo():
    print("Hello there.")

telegram.add_command("hello", foo)

# Always set the start_loop(blocking=True) at the end of
# your code. You need it, that the commands work.
telegram.start_loop(blocking=True)

```


```python
# Add a confirmation command to your bot.
...
def important():
    telegram.send_msg("You wanted to run this function.")
    
telegram.add_confirmation_command("important", important)
...
```

```python
# Retrieve arguments from command, e.g. type '/what stuff'
...
def command_with_args(update, context):
    try:
        arg = context.args[0]
    except IndexError:
        arg = 'crazy'
    telegram.double_log_msg(f"This is {arg} stuff my friend.")
    
 telegram.add_command("what", command_with_args)
...
```
```python
# If blocking is set to False, the telegram loop works
# as long as the main thread is alive.
telegram.start_loop(blocking=False)
# <Your code>
# If you don't need commands anymore, you can stop the loop.
telegram.stop_loop()
```
```python
# predefined functions are:
/info, /stop, /restart and /help
```
## Client Configuration
```
**kwargs of Client:
----------------------------
- bot_token=<TELEGRAM-TOKEN>  # is required to allow a connection to a bot
- save_token=False # if you set it to True, it will save your token in config.ini - file for easier use
- chat_id=None # provide chat_id for specific chat
- log_lvl=logging.DEBUG # set the logging level of you bot
- log_stderr=False # redirect stderr output to display in bot
- other_logger=None  # redirect other_logger output to display in bot
- encrypt_vars=False # if set to True, you can give an key [with the help of environment_var] to encrypt token and chat_id
- environment_var # name of the environment variable
```
## Exceptions
>This error happens if you run more than one Client connection.
> 
![error-getUpdates_2023-04-03_21-16-18.jpg](fbratelegram%2Fexamples%2Ferror-getUpdates_2023-04-03_21-16-18.jpg)
## Donations
```python
BTC: 'bc1qed0e8ej4nmyz88sy5zzwvrjfkft0y5aca7cqyw'
ETH: '0x987f26cB65DD4704Fa0b9d722f4515e2AA36eEF0'
```
