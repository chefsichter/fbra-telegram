from configparser import ConfigParser
from fbracrypto.crypto import Crypto


class FBraConfigParser(ConfigParser):
    CONFIG_CHAT_ID = 'chat_id'
    CONFIG_TOKEN = 'token'
    CONFIG_MAIN = 'main'
    CONFIG_FILE = 'config.ini'

    def __init__(self, encrypt=False, environment_var=""):
        super().__init__()
        if not self.read_config():
            self.create_config_file()
        self.encrypt = encrypt
        if encrypt:
            self.env_var = environment_var
            self.crypto = Crypto(environment_var=self.env_var)

    def write_config_file(self):
        with open(self.CONFIG_FILE, 'w') as f:
            self.write(f)

    def read_config(self):
        return self.read(self.CONFIG_FILE)

    def set_key(self, key, value):
        self.read_config()
        self.set(self.CONFIG_MAIN, key, value)
        self.write_config_file()

    def get_key(self, key):
        self.read_config()
        return self.get(self.CONFIG_MAIN, key)

    def get_chat_id(self):
        chat_id = self.get_key(self.CONFIG_CHAT_ID)
        if self.encrypt:
            chat_id = self.crypto.get_plain_value(chat_id)
        return chat_id

    def set_chat_id(self, value):
        if self.encrypt:
            value = self.crypto.cipher(value)
        self.set_key(self.CONFIG_CHAT_ID, value)

    def get_token(self):
        token = self.get_key(self.CONFIG_TOKEN)
        if self.encrypt:
            token = self.crypto.get_plain_value(token)
        return token

    def set_token(self, value):
        if self.encrypt:
            value = self.crypto.cipher(value)
        self.set_key(self.CONFIG_TOKEN, value)

    def create_config_file(self):
        self.read(self.CONFIG_FILE)
        self.add_section(self.CONFIG_MAIN)
        self.set_key(self.CONFIG_TOKEN, '')
        self.set_key(self.CONFIG_CHAT_ID, '')
        self.write_config_file()
