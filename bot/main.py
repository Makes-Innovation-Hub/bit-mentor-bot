import os
import requests
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes,CallbackQueryHandler
import logging.config
from bot.config.logging_config import logging_config
from bot.handlers.basic_handlers import *
from bot.handlers.question_handlers import *
from bot.handlers.user_handlers import *
from bot.handlers.youtube_handler import mark_video_watched_callback
from bot.setting.config import *

# Configure logging
from bot.utils.public_ip import get_public_ip
from bot.handlerConversation.youtubeConversation import youtube_conversation

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


# Main function
def main():
    logger.info("Starting bot application")
    public_ip = get_public_ip()
    try:
        BOT_TOKEN = config.BOT_TOKEN
        if BOT_TOKEN:
            application = Application.builder().token(BOT_TOKEN).build()

            # basic
            start_handler = CommandHandler('start', lambda update, context: start(update, context, public_ip))
            connect_handler = CommandHandler('connect', connect)
            help_handler = CommandHandler('help', help_command)

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
            # youtube
            application.add_handler(youtube_conversation())
            application.add_handler(CallbackQueryHandler(mark_video_watched_callback))

            application.add_handler(conv_handler)
            application.add_handler(start_handler)
            application.add_handler(connect_handler)
            application.add_handler(help_handler)

            logger.info("Bot handlers added and polling started")
            application.run_polling()
        else:
            raise Exception("BOT_TOKEN not loaded correctly as env var")
    except Exception as e:

        logger.error("Error in loading BOT_TOKEN", exc_info=True)
        raise e


if __name__ == '__main__':
    main()
