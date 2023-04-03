import asyncio
import inspect
import logging
import os
import re
import signal
import sys
import threading
import time
import traceback
from inspect import signature

import telegram
import telegram.error
from telegram import BotCommand, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes

from fbra_telegram.extras.config_parser import FBraConfigParser
from fbra_telegram.extras.stderr_logger import StderrLogger

LOGGER_NAME = "fbra-telegram"


class Client:
    def __init__(self,
                 bot_token=None,
                 save_token=False,
                 chat_id=None,
                 log_lvl=logging.DEBUG,
                 log_stderr=False,
                 other_logger=None):
        super().__init__()
        self.modul = f"{self.__class__.__name__}"
        self.ini = FBraConfigParser()
        self.token = bot_token if bot_token is not None else self.ini.get_token()
        self.app, self.bot, self.updater, self.loop = self._build_application()
        self.msgs = Messages(client=self, bot=self.bot, ini=self.ini, log_lvl=log_lvl)
        if self.token is None:
            self.msgs.console.warning(f"{self.modul}: You have to set the telegram token as an argument or update the "
                                      f"token value in config.ini.")
        else:
            if save_token:
                self.ini.set_token(self.token)
            if log_stderr:
                self.msgs.addHandler_to_stderr()
            if other_logger:
                other_logger.addHandler(self)
            # initialize asyncio python-telegram-bot
            if chat_id:
                self.chat_id = chat_id
            else:
                self.chat_id = self.msgs.restore_chat_id()
            self.cmds = Commands(client=self, app=self.app, valid_chat_filter=self.msgs.valid_chat_filter)
            self.app.add_error_handler(self.msgs.error_handler)
            self.main_thread = threading.main_thread()
            self.telegram_thread = None
            # self.msgs.double_log_msg("Bot initialized...")

    def _build_application(self):
        loop = asyncio.new_event_loop()
        builder = ApplicationBuilder()
        builder.token(self.token)
        builder.connect_timeout(10)
        builder.read_timeout(10)
        app = builder.build()
        bot = app.bot
        updater = app.updater
        return app, bot, updater, loop

    def add_command(self, command, callback):
        self.cmds.add_command(command, callback)

    def add_confirmation_command(self, command, callback, confirm_msg=None):
        self.cmds.add_confirmation_command(command, callback, confirm_msg)

    def run_async(self, func, *args, **kwargs):
        if self.loop.is_running():
            return self.loop.create_task(func(*args, **kwargs))
            # return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self.loop)
        else:
            return self.loop.run_until_complete(func(*args, **kwargs))

    def send_msg(self, msg, **kwargs):
        self.msgs.send_msg(msg, **kwargs)

    def double_log_msg(self, msg):
        self.msgs.double_log_msg(msg)

    @staticmethod
    async def start__command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot is running.")

    def _stop_helper_func(self, helper_func):
        self.stop_loop()
        helper_func()

    def _restart_process(self):
        self.msgs.double_log_msg("Bot restarted.")
        executable = sys.executable
        os.execv(executable, ['python3'] + sys.argv)

    def restart__command(self, update, context):
        self.msgs.double_log_msg("Bot is restarting...")
        threading.Thread(target=self._stop_helper_func,
                         args=(self._restart_process,),
                         daemon=False).start()

    def _terminate_process(self):
        self.msgs.double_log_msg("Bot stopped.")
        os.kill(os.getpid(), signal.SIGTERM)

    def stop__command(self, update, context):
        self.msgs.double_log_msg("Bot is stopping...")
        threading.Thread(target=self._stop_helper_func,
                         args=(self._terminate_process,),
                         daemon=False).start()

    def help__command(self, update, context):
        commands = self.cmds.get_commands_from_dispatcher()
        com_str = ""
        for c in commands:
            com_str += "\n/" + c
        self.msgs.send_msg(msg=com_str)

    def _app_run_polling_in_thread(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.app.initialize())
        self.loop.run_until_complete(self.updater.start_polling())  # one of updater.start_webhook/polling
        self.loop.run_until_complete(self.app.start())
        # self.msgs.double_log_msg("Bot update loop has started...")
        self.loop.run_forever()

    def start_loop(self):
        self.telegram_thread = threading.Thread(target=self._app_run_polling_in_thread, daemon=False)
        self.telegram_thread.start()

    def update_modules(self, app, bot):
        self.cmds.client, self.cmds.app = (self, app)
        self.msgs.client, self.msgs.bot = (self, bot)

    def stop_loop(self):
        time.sleep(2)
        self.loop.stop()
        self.telegram_thread.join()
        try:
            if self.updater.running:
                self.loop.run_until_complete(self.updater.stop())
            if self.app.running:
                self.loop.run_until_complete(self.app.stop())
            self.loop.run_until_complete(self.app.shutdown())
        finally:
            self.loop.close()
        self.app, self.bot, self.updater, self.loop = self._build_application()
        self.update_modules(self.app, self.bot)
        # self.msgs.double_log_msg("Bot update loop has stopped...")


class Messages(logging.Handler):
    def __init__(self, client, bot, ini, log_lvl):
        super().__init__()
        self.modul = f"{self.__class__.__name__}"
        self.client = client
        self.bot = bot
        self.ini = ini
        self.log_lvl = log_lvl
        self._initialize_bot_logger()
        self.default_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        self.console = self._initialize_console_logger()
        if not self.ini.read_config():
            self.ini.create_config_file()
        self.updates = self.client.run_async(self.bot.get_updates)
        self.chat_id = self.restore_chat_id()
        self.valid_chat_filter = filters.COMMAND & filters.Chat(chat_id=int(self.chat_id))

    def restore_chat_id(self):
        chat_id = self.ini.get_chat_id()
        if chat_id != "":
            return chat_id
        else:
            try:
                chat_id = str(self.updates[0].message.from_user.id)
                self.ini.set_chat_id(chat_id)
                return chat_id
            except IndexError:
                self.console.warning(f"{self.modul}: The 'chat id' couldn't be restored. "
                                     f"Please send the message '/start' in the bot chat.")
                os.kill(os.getpid(), signal.SIGTERM)

    def _initialize_bot_logger(self):
        self.setFormatter(logging.Formatter('%(message)s'))
        self.setLevel(self.log_lvl)

    def _initialize_console_logger(self):
        log = logging.getLogger(LOGGER_NAME)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(self.default_format))
        log.addHandler(stream_handler)
        log.setLevel(self.log_lvl)
        return log

    def addHandler_to_stderr(self):
        stdr_logger = StderrLogger()
        stdr_logger.logger.addHandler(self)  # will output stderr to the bot

    def send_msg(self, msg, **kwargs):
        try:
            if len(msg) > 4096:
                for x in range(0, len(msg), 4096):
                    self.client.run_async(self.bot.send_message, self.chat_id, msg[x:x + 4096], **kwargs)
            else:
                self.client.run_async(self.bot.send_message, self.chat_id, msg, **kwargs)
        except telegram.error.TelegramError as error:
            self._double_log_error(error)
            if isinstance(error, (telegram.error.TimedOut, telegram.error.NetworkError)):  # "Bad Gateway", "Timed out"
                time.sleep(1)

    def double_log_msg(self, msg):
        self.console.info(msg)
        self.send_msg(msg)

    def emit(self, record):
        """
        Messages class is a handler for the connected loggers
        It will redirect those messages to the telegram bot
        """
        msg = self.format(record)
        self.send_msg(msg=msg)

    def _create_err_string(self, error):
        tb_list = traceback.format_exception(None, error, error.__traceback__)
        tb_string = ''.join(tb_list)
        err_str = f"{self.modul}: The following error was raised: \n{tb_string}"
        return err_str

    def _double_log_error(self, error):
        try:
            err_str = self._create_err_string(error)
            self.console.error(err_str)
            self.send_msg(str(error))
        except Exception:
            pass

    async def error_handler(self, update, context):
        self._double_log_error(context.error)


class Commands:
    FBRA_COMMAND = "__command"
    CONFIRM_MSG = "Shall i run the following command?"

    def __init__(self, client, app: telegram.ext.Application, valid_chat_filter):
        self.client = client
        self.app = app
        self.valid_chat_filter = valid_chat_filter
        self.set_up_all_commands()

    def _add_simple_commands_to_app(self):
        cmds_in_client = {method: self.client.__class__ for method in self.client.__class__.__dict__.keys()
                          if method.endswith(self.FBRA_COMMAND)}
        cmds_in_cmds = {method: self.__class__ for method in self.__class__.__dict__.keys()
                        if method.endswith(self.FBRA_COMMAND)}
        commands = dict(cmds_in_cmds, **cmds_in_client)
        for method, cls in commands.items():
            command = method.replace(self.FBRA_COMMAND, '')
            callback = getattr(cls, method)
            self.add_command(command, callback)

    def get_commands_from_dispatcher(self):
        commands = []
        for item in self.app.handlers.get(0):
            if isinstance(item, CommandHandler):
                commands.append(list(item.commands)[0])
            elif isinstance(item, ConversationHandler):
                commands.append(list(item._entry_points[0].commands)[0])
        return commands

    def _inform_server_about_cmds(self):
        commands = self.get_commands_from_dispatcher()
        com_obj_list = []
        for command in commands:
            com_obj = BotCommand(command=command, description=f"command: {command}")
            com_obj_list.append(com_obj)
        self.client.run_async(self.app.bot.set_my_commands, com_obj_list)

    def set_up_all_commands(self):
        self._add_simple_commands_to_app()
        self._inform_server_about_cmds()

    @staticmethod
    def has_parameter(obj, attr):
        try:
            value = obj[attr]
            return True
        except KeyError:
            return False

    def _create_callback_func(self, func):
        paras = signature(func).parameters

        def callback_func(update, context):
            if len(paras) == 3:
                func(self.client, update, context)
            elif len(paras) == 2:
                func(update, context)
            elif self.has_parameter(paras, "update"):
                func(update)
            elif self.has_parameter(paras, "context"):
                func(context)
            else:
                func()

        return callback_func

    @staticmethod
    def _wrap_func_with_async(func):
        async def async_func(update, context):
            return func(update, context)

        return async_func

    def add_command(self, command, callback):
        if not inspect.iscoroutinefunction(callback):
            callback_func = self._create_callback_func(callback)
            callback_func = self._wrap_func_with_async(callback_func)
        else:
            callback_func = callback
        self.app.add_handler(CommandHandler(command=command,
                                            callback=callback_func,
                                            filters=self.valid_chat_filter))

    async def show_buttons_yes_or_no(self, update, context):
        buttons = ReplyKeyboardMarkup([[KeyboardButton("Yes"), KeyboardButton('No')]],
                                      one_time_keyboard=True,
                                      resize_keyboard=True)
        await update.message.reply_text(text=f"{self.CONFIRM_MSG}\n{update.message.text}",
                                        reply_markup=buttons)
        return 0  # in waiting state

    @staticmethod
    async def end_conversation_handler(update, context):
        return ConversationHandler.END

    @staticmethod
    def _create_confirmation_func(func):
        def wrapper(update, context):
            if update.message.text.lower() in ['yes', 'y']:
                func(update, context)
            else:
                pass
            # self.client.run_async(update.message.reply_text, f"Okay!",
            #                       reply_markup=telegram.ReplyKeyboardRemove()
            #                       )
            return ConversationHandler.END

        return wrapper

    def add_confirmation_command(self, command, callback, confirmation_msg=None):
        if confirmation_msg:
            self.CONFIRM_MSG = confirmation_msg
        callback_func = self._create_callback_func(callback)
        callback_func = self._create_confirmation_func(callback_func)
        callback_func = self._wrap_func_with_async(callback_func)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler(command=command,
                                         callback=self.show_buttons_yes_or_no,
                                         filters=self.valid_chat_filter)],
            states={
                0: [MessageHandler(filters.Regex(re.compile(r'^(yes|no|y|n)$', re.IGNORECASE)),
                                   callback=callback_func)]
            },
            fallbacks=[CommandHandler('end_conversation', self.end_conversation_handler)],
        )
        self.app.add_handler(conv_handler)

    def add_reply_to_command(self, obj, command):
        callback = getattr(obj, f"{command}")
        self.app.add_handler(CommandHandler(command=command,
                                            callback=callback,
                                            filters=self.valid_chat_filter))
