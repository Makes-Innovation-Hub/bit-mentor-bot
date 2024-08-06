from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters

from bot.handlers.basic_commands import cancel
from bot.handlers.youtube_handler import start_youtube, get_video_length, get_topic

TOPIC2, VIDEO_LENGTH = range(2)


def youtube_conversation():
    youtube_conv = ConversationHandler(
        entry_points=[CommandHandler('youtube', start_youtube)],
        states={
            TOPIC2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_topic)],
            VIDEO_LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_video_length)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    return youtube_conv
