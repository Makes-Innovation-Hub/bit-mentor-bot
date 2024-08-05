import requests
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from bot.handlers.basic_fns import start, connect, help, question_command, difficulty_response, answers_response, \
    topic_response, user_answer_response, cancel
from bot.handlers.youtube_handler import  start_youtube, get_topic, get_video_length, VIDEO_LENGTH
from bot.setting.config import config

DIFFICULTY, ANSWERS, TOPIC, USER_ANSWER = range(4)
TOPIC2, VIDEO_LENGTH = range(2)

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
            help_handler = CommandHandler('help', lambda update, context: help(update, context))
            conv_handler = ConversationHandler(
                entry_points=[CommandHandler('question', question_command)],
                states={
                    DIFFICULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, difficulty_response)],
                    ANSWERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, answers_response)],
                    TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, topic_response)],
                    USER_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_answer_response)],
                },
                fallbacks=[CommandHandler('cancel', cancel)],
            )
            youtube_conv_handler = ConversationHandler(
                entry_points=[CommandHandler('youtube', start_youtube)],
                states={
                    TOPIC2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_topic)],
                    VIDEO_LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_video_length)],
                },
                fallbacks=[CommandHandler('cancel', cancel)],
            )
            application.add_handler(youtube_conv_handler)
            application.add_handler(conv_handler)
            application.add_handler(start_handler)
            application.add_handler(connect_handler)
            application.add_handler(help_handler)

            # Start the Bot
            application.run_polling()
        else:
            raise Exception("BOT_TOKEN not loaded correctly as env var")
    except Exception as e:
        print("error in loading BOT_TOKEN", e)
        return e


if __name__ == '__main__':
    main()
