from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import dotenv
import os
import logging
import requests

from src.logging.logging_config import setup_logging

class Bot:
    def __init__(self):
        dotenv.load_dotenv()
        self.token = os.getenv('TELEGRAM')
        setup_logging()
        self.logger = logging.getLogger()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            self.logger.info("Sending start message")
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Hello! I am a bot & i can help you with identifying you public IP!')
        except Exception as e:
            self.logger.error(f"Error occurred in start function: {e}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            self.logger.info("Sending help message")
            help_text = "You can control me by sending these commands:\n"
            help_text += "/ip - Returns the public ip addess\n"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)
        except Exception as e:
            self.logger.error(f"Error occurred in help_command function: {e}")

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            self.logger.info("Echoing message")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Yolo")
        except Exception as e:
            self.logger.error(f"Error occurred in echo function: {e}")

    async def get_ip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            self.logger.info("Getting IP address")
            ip = requests.get('https://api.ipify.org').text
            await context.bot.send_message(chat_id=update.effective_chat.id, text=ip)
        except Exception as e:
            self.logger.error(f"Error occurred in get_ip function: {e}")

    def run(self) -> None:
        try:
            self.logger.info("Bot started")
            application = ApplicationBuilder().token(self.token).build()

            start_handler = CommandHandler('start', self.start)
            application.add_handler(CommandHandler('help', self.help_command))
            application.add_handler(CommandHandler('ip', self.get_ip))

            echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo)

            application.add_handler(start_handler)
            application.add_handler(echo_handler)

            application.run_polling()
        except Exception as e:
            self.logger.error(f"Error occurred in run function: {e}")

if __name__ == '__main__':
    bot = Bot()
    bot.run()
