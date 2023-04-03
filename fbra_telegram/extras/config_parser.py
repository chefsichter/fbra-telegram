from configparser import ConfigParser


class FBraConfigParser(ConfigParser):
    CONFIG_CHAT_ID = 'chat_id'
    CONFIG_TOKEN = 'token'
    CONFIG_MAIN = 'main'
    CONFIG_FILE = 'config.ini'

    def __init__(self):
        super().__init__()

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
        return self.get_key(self.CONFIG_CHAT_ID)

    def set_chat_id(self, value):
        self.set_key(self.CONFIG_CHAT_ID, value)

    def get_token(self):
        return self.get_key(self.CONFIG_TOKEN)

    def set_token(self, value):
        self.set_key(self.CONFIG_TOKEN, value)

    def create_config_file(self):
        self.read(self.CONFIG_FILE)
        self.add_section(self.CONFIG_MAIN)
        self.set_key(self.CONFIG_TOKEN, '')
        self.set_key(self.CONFIG_CHAT_ID, '')
        self.write_config_file()

