import requests
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, \
    CallbackQueryHandler

from bot.handlers.basic_commands import cancel, start, help
from bot.handlers.question_handler import connect
from bot.handlers.youtube_handler import button_callback
from bot.setting.config import config
from bot.utils.public_ip import get_public_ip
from handlerConversation.questionConversation import question_conversation
from handlerConversation.youtubeConversation import youtube_conversation



def main():
    public_ip = get_public_ip()

    try:
        BOT_TOKEN = config.BOT_TOKEN
        if BOT_TOKEN:
            application = Application.builder().token(BOT_TOKEN).build()

            # basic
            application.add_handler(CommandHandler('start', lambda update, context: start(update, context, public_ip)))
            application.add_handler(CommandHandler('connect', lambda update, context: connect(update, context)))
            application.add_handler(CommandHandler('help', lambda update, context: help(update, context)))

            # youtube
            application.add_handler(youtube_conversation())
            application.add_handler(CallbackQueryHandler(button_callback))

            # question
            application.add_handler(question_conversation())

            application.run_polling()
        else:
            raise Exception("BOT_TOKEN not loaded correctly as env var")
    except Exception as e:
        print("error in loading BOT_TOKEN", e)
        return e


if __name__ == '__main__':
    main()
