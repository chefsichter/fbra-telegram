import os
import sys
import threading
import time
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

from client import TelegramClient

from extras.config_parser import FBraConfigParser
from test_keys import bot_token, chat_id


class TestTelegramClient(TestCase):
    org_token = "1234"

    @classmethod
    def setUpClass(cls) -> None:
        cls.ini = FBraConfigParser()

    # def tearDown(self) -> None:
    #     try:
    #         os.remove(self.ini.CONFIG_FILE)
    #     except FileNotFoundError:
    #         pass

    def test_create_config_ini(self):
        self.ini.create_config_file()
        self.assertTrue(os.path.isfile(self.ini.CONFIG_FILE))

    def test_get_token(self):
        self.ini.create_config_file()
        self.ini.set_token(self.org_token)
        token = self.ini.get_token()
        self.assertEqual(token, self.org_token)

    def test_storing_token(self):
        with patch('client.TelegramClient._build_application') as mock:
            mock.return_value = Mock(return_value=[Mock(), Mock(), Mock(), Mock()])
            telegram = TelegramClient(save_token=True,
                                      bot_token=self.org_token)
            token = telegram.ini.get_token()
            self.assertEqual(self.org_token, token)

    def test_save_bot_token(self):
        client = TelegramClient(save_token=True, bot_token=bot_token)
        token = client.ini.get_token()
        self.assertTrue(token != "")

    def test_starting_telegram_client(self):
        client = TelegramClient(bot_token=bot_token, chat_id=chat_id)
        client.start_loop()
        self.assertTrue(client.loop.is_running())
        time.sleep(1)
        client.stop_loop()
        # client.stop_helper_func(lambda: client.console.debug("Loop has stopped"))

    def test_stderr_output(self):
        client = TelegramClient(bot_token=bot_token, chat_id=chat_id, log_stderr=True)
        client.start_loop()
        time.sleep(1)
        sys.stderr.write("An error was raised")

        def err_func():
            time.sleep(1)
            5 / 0

        threading.Thread(target=err_func).start()
        time.sleep(10)
        client.stop_loop()

    def test_send_empty(self):
        client = TelegramClient(bot_token=bot_token, chat_id=chat_id, log_stderr=True)

        def empty_msg():
            client.send_msg("\n")

        threading.Thread(target=empty_msg).start()
        time.sleep(2)
        client.send_msg(" ")
        time.sleep(2)
        client.send_msg("")
        time.sleep(5)

    def test_stop__command(self):
        client = TelegramClient(bot_token=bot_token, chat_id=chat_id, log_stderr=True)
        client.start_loop()
        time.sleep(3)
        client.run_async(client.stop__command, None, None)
        time.sleep(20)

    def test_restart__command(self):
        client = TelegramClient(bot_token=bot_token, chat_id=chat_id, log_stderr=True)
        client.start_loop()
        time.sleep(3)
        client.run_async(client.restart__command, None, None)
        time.sleep(20)

    def test_add_command(self):
        client = TelegramClient(bot_token=bot_token, chat_id=chat_id, log_stderr=True)
        client.start_loop()

        def hello_world():
            client.double_log_msg('hello world')

        client.add_command("hello_world", hello_world)

        def hello_world2(context):
            arg = context.args[0]
            client.double_log_msg(f'hello world {arg}')

        client.add_command("hello_world2", hello_world2)
        time.sleep(60)
        client.stop_loop()

    def test_add_confirmation_command(self):
        client = TelegramClient(bot_token=bot_token, chat_id=chat_id, log_stderr=True)
        client.start_loop()

        def important():
            client.double_log_msg('important')

        client.add_confirmation_command("important", important)
        client.add_confirmation_command("important2", important, "Soll ich das jetzt ausführen?")
        time.sleep(60)
        client.stop_loop()


