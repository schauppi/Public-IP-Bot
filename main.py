from src.telegram.TelegramBot import Bot

if __name__ == "__main__":
    try:
        bot = Bot()
        bot.run()
    except Exception as e:
        print(f"An error occurred: {e}")
