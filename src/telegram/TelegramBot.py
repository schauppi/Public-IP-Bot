from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
import dotenv
import os
import logging
import httpx
from requests.exceptions import RequestException
import asyncio

from src.logging.logging_config import setup_logging


class Bot:
    """
    Telegram bot that can fetch the public IP address of the user and poll for IP changes every 5 minutes.

    Methods:

    fetch_ip: Fetches the public IP address of the user.
    fetch_initial_ip: Fetches the initial IP address of the user.
    start: Sends a start message to the user.
    help_command: Sends a help message to the user.
    echo: Echoes the message sent by the user.
    poll_ip_command: Starts polling for IP changes every 5 minutes.
    poll_ip: Polls for IP changes every 5 minutes.
    get_ip: Gets the IP address of the user.
    set_poll_command: Sets the polling time.
    stop_poll_ip_command: Stops polling for IP changes.
    status_command: Sends the status of the polling and the current polling time.
    run: Runs the bot.
    """

    def __init__(self):
        dotenv.load_dotenv()
        self.token = os.getenv("TELEGRAM")
        setup_logging()
        self.logger = logging.getLogger()
        self.current_ip = None
        self.poll_time = 300

    async def fetch_ip(self):
        """
        Fetches the public IP address of the user.

        Args:
            None

        Returns:
            str: The public IP address of the user.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("https://api.ipify.org")
                response.raise_for_status()
                return response.text
            except httpx.RequestError as e:
                self.logger.error(f"Failed to fetch IP: {e}")
                return None

    async def fetch_initial_ip(self):
        """
        Fetches the initial IP address of the user.

        Args:
            None

        Returns:
            None
        """
        try:
            self.current_ip = await self.fetch_ip()
            self.logger.info(f"Initial IP fetched: {self.current_ip}")
        except Exception as e:
            self.logger.error(f"Failed to fetch initial IP: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Sends a start message to the user.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.

        Returns:
            None
        """
        self.logger.info("Sending start message")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello! I am a bot & i can help you with identifying your public IP!",
        )

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Sends a help message to the user.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.

        Returns:
            None
        """
        self.logger.info("Sending help message")
        help_text = "You can control me by sending these commands:\n"
        help_text += "/ip - Returns the public ip address\n"
        help_text += "/start_poll_ip - Polls for IP changes every 5 minutes\n"
        help_text += "/stop_poll_ip - Stops polling for IP changes\n"
        help_text += "/set_poll <time> - Sets the polling time\n"
        help_text += (
            "/status - Sends the status of the polling and the current polling time\n"
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Echoes the message sent by the user.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.

        Returns:
            None
        """
        self.logger.info("Echoing message")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Yolo")

    async def poll_ip_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Starts polling for IP changes every 5 minutes.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.

        Returns:
            None
        """
        try:
            self.logger.info("Starting IP polling")
            self.chat_id = update.effective_chat.id
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=f"I will now check for IP changes every {self.poll_time} seconds or {round(self.poll_time/60, 2)} minutes.",
            )
            asyncio.create_task(self.poll_ip(context))
        except Exception as e:
            self.logger.error(f"Failed to start IP polling: {e}")

    async def poll_ip(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Polls for IP changes every 5 minutes.

        Args:
            context (ContextTypes.DEFAULT_TYPE): The context object.

        Returns:
            None
        """
        while True:
            try:
                new_ip = await self.fetch_ip()
                if new_ip and new_ip != self.current_ip:
                    self.current_ip = new_ip
                    await context.bot.send_message(
                        chat_id=self.chat_id, text=f"Your new public IP is: {new_ip}"
                    )
            except asyncio.CancelledError:

                self.logger.info("IP polling has been cancelled.")
                break
            except Exception as e:
                self.logger.error(f"Failed during IP polling: {e}")
            await asyncio.sleep(self.poll_time)

    async def get_ip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Gets the IP address of the user.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.

        Returns:
            None
        """
        self.logger.info("Getting IP address")
        try:
            ip = await self.fetch_ip()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=ip)
        except RequestException as e:
            self.logger.error(f"Failed to get IP address: {e}")
            raise

    async def set_poll_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Sets the polling time.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.

        Returns:
            None
        """
        try:
            args = context.args
            if len(args) != 1:
                raise ValueError("You must provide exactly one argument.")
            new_poll_time = int(args[0])
            if new_poll_time <= 0:
                raise ValueError("The polling time must be a positive integer.")

            self.poll_time = new_poll_time

            if hasattr(self, "poll_task") and not self.poll_task.done():
                self.poll_task.cancel()
            self.poll_task = asyncio.create_task(self.poll_ip(context))
            self.logger.info(
                f"Polling time set to {self.poll_time} seconds or {round(self.poll_time/60, 2)} minutes."
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Polling time has been set to {self.poll_time} seconds or {round(self.poll_time/60, 2)} minutes.",
            )
        except Exception as e:
            self.logger.error(f"Failed to set polling time: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=str(e)
            )

    async def stop_poll_ip_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Stops polling for IP changes.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.

        Returns:
            None
        """
        try:
            self.logger.info("Stopping IP polling")
            if hasattr(self, "poll_task") and not self.poll_task.done():
                self.poll_task.cancel()
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="IP polling has been stopped."
            )
        except Exception as e:
            self.logger.error(f"Failed to stop IP polling: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=str(e)
            )

    async def status_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Sends the status of the polling and the current polling time.

        Args:
            update (Update): The update object.
            context (ContextTypes.DEFAULT_TYPE): The context object.

        Returns:
            None
        """
        try:
            self.logger.info("Sending status")
            status = (
                "Polling is currently running."
                if hasattr(self, "poll_task") and not self.poll_task.done()
                else "Polling is currently stopped."
            )
            status += f" The current polling time is {self.poll_time} seconds or {round(self.poll_time/60, 2)} minutes."
            status += f" The current IP is {self.current_ip}."
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=status
            )
        except Exception as e:
            self.logger.error(f"Failed to send status: {e}")

    def run(self) -> None:
        """
        Runs the bot.

        Args:
            None

        Returns:
            None
        """
        self.logger.info("Running bot")
        application = ApplicationBuilder().token(self.token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("ip", self.get_ip))
        application.add_handler(CommandHandler("start_poll_ip", self.poll_ip_command))
        application.add_handler(CommandHandler("set_poll", self.set_poll_command))
        application.add_handler(
            CommandHandler("stop_poll_ip", self.stop_poll_ip_command)
        )
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo)
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetch_initial_ip())
        application.run_polling()
