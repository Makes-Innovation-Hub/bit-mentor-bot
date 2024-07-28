import os
import requests
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from bot.handlers.basic_fns import start, connect
from setting.config import *


# Load environment variables from .env file


def get_public_ip():
    response = requests.get('https://api.ipify.org?format=json')
    response.raise_for_status()
    return response.json()['ip']


def main():
    # Fetch the public IP address
    public_ip = get_public_ip()

    # Create the Application and pass it your bot's token
    try:
        BOT_TOKEN = config.BOT_TOKEN
        if BOT_TOKEN:
            application = Application.builder().token(BOT_TOKEN).build()
            # Register the /start command with the start function
            start_handler = CommandHandler('start', lambda update, context: start(update, context, public_ip))
            connect_handler = CommandHandler('connect', lambda update, context: connect(update, context))

            application.add_handler(start_handler)
            application.add_handler(connect_handler)

            # Start the Bot
            application.run_polling()
        else:
            raise Exception("BOT_TOKEN not loaded correctly as env var")
    except Exception as e:
        print("error in loading BOT_TOKEN", e)
        return e


if __name__ == '__main__':
    main()
