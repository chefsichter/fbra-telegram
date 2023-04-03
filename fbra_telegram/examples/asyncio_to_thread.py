import asyncio
import threading
import time

from telegram import Update
import telegram.error
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


class ThreadTelegram:
    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.token = bot_token
        self.chat_id = chat_id
        self.app, self.bot, self.updater, self.loop = self._build_application()
        self.telegram_thread = None
        self.app.add_handler(CommandHandler(command='start',
                                            callback=self.start))
        print("Bot initialized...")

    def _build_application(self):
        loop = asyncio.new_event_loop()
        builder = ApplicationBuilder()
        builder.token(self.token)
        app = builder.build()
        return app, app.bot, app.updater, loop

    def run_async(self, func, *args, **kwargs):
        if self.loop.is_running():
            return self.loop.create_task(func(*args, **kwargs))
            # return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self.loop)
        else:
            return self.loop.run_until_complete(func(*args, **kwargs))

    def send_msg(self, msg, **kwargs):
        try:
            if len(msg) > 4096:
                for x in range(0, len(msg), 4096):
                    self.run_async(self.bot.send_message, self.chat_id, msg[x:x + 4096], **kwargs)
            else:
                self.run_async(self.bot.send_message, self.chat_id, msg, **kwargs)
        except telegram.error.TelegramError as error:
            pass

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot is running.")

    def _app_run_polling_in_thread(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.app.initialize())
        self.loop.run_until_complete(self.updater.start_polling())
        self.loop.run_until_complete(self.app.start())
        print("Bot update loop has started...")
        self.loop.run_forever()

    def start_loop(self):
        self.telegram_thread = threading.Thread(target=self._app_run_polling_in_thread, daemon=False)
        self.telegram_thread.start()

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
        print("Bot update loop has stopped...")


if __name__ == '__main__':
    from tests.test_keys import bot_token, chat_id

    client = ThreadTelegram(bot_token=bot_token, chat_id=chat_id)
    client.send_msg("Hello world")
    client.start_loop()
    # try out /start command
    time.sleep(60)
    client.stop_loop()
