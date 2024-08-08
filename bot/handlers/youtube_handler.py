import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes

from constants import CATEGORIES

YOUTUBE_TOPIC, VIDEO_LENGTH = range(2)


async def start_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    categories_text = "\n".join(CATEGORIES)
    message_text = f"Please select a topic from the following categories:\n{categories_text}"

    reply_keyboard = [[category] for category in CATEGORIES]
    await update.message.reply_text(
        f"{message_text}",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return YOUTUBE_TOPIC


async def get_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_topic = update.message.text
    if selected_topic not in CATEGORIES:
        await update.message.reply_text(
            f"'{selected_topic}' is not a valid topic. Please select a topic from the following categories:\n" + "\n".join(
                CATEGORIES))
        return YOUTUBE_TOPIC

    context.user_data['topic'] = selected_topic
    await update.message.reply_text("Please enter the video length (short, medium, long):")
    return VIDEO_LENGTH


async def get_video_length(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    video_length = update.message.text
    topic = context.user_data.get('topic', "")
    user_id = update.message.from_user.id

    if video_length not in ["short", "medium", "long"]:
        await update.message.reply_text("Invalid length. Please enter 'short', 'medium', or 'long':")
        return VIDEO_LENGTH
    print(video_length,topic,user_id)
    try:
        response = requests.get(f"http://localhost:8000/youtube/?topic={topic}&video_length={video_length}")
        response.raise_for_status()
        video_links = response.json()
        # video_links = [
        #     "https://www.youtube.com/watch?v=fake10",
        #     "https://www.youtube.com/watch?v=fake7",
        #     "https://www.youtube.com/watch?v=fake3",
        #     "https://www.youtube.com/watch?v=fake4",
        #     "https://www.youtube.com/watch?v=fake5"
        # ]
        if not video_links:
            await update.message.reply_text("No videos found.")
            return ConversationHandler.END

        reply_text = "Here are the top YouTube videos:\n\n" + "\n".join(video_links)
        await update.message.reply_text(reply_text)

    except requests.HTTPError as e:
        await update.message.reply_text(f"Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

    return ConversationHandler.END


async def mark_video_watched_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass