from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import dotenv
import os

class Bot:
    def __init__(self):
        dotenv.load_dotenv()
        self.token = os.getenv('TELEGRAM')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Hello! I am a bot & i can help you with identifying you public IP!')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        help_text = "You can control me by sending these commands:\n"
        help_text += "/ip - Returns the public ip addess\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Yolo")

    def run(self) -> None:
        application = ApplicationBuilder().token(self.token).build()

        start_handler = CommandHandler('start', self.start)
        application.add_handler(CommandHandler('help', self.help_command))

        echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo)

        application.add_handler(start_handler)
        application.add_handler(echo_handler)

        application.run_polling() 

if __name__ == '__main__':
    bot = Bot()
    bot.run()