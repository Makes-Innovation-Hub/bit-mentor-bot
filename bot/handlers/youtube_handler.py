import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes

from bot.config.logging_config import app_logger
from constants import CATEGORIES
from bot.utils.youtube_utils import *

YOUTUBE_TOPIC, VIDEO_LENGTH = range(2)


async def start_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Starts the YouTube video selection process.

    Returns:
        int: The next state of the conversation.

    Raises:
        Exception: If an error occurs during the YouTube video selection process.

    """
    try:
        context.user_data["operation"] = "youtube command"
        app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) started YouTube video selection.")
        await send_category_selection(update)
        return YOUTUBE_TOPIC
    except Exception as e:
        app_logger.error(f"Error in start_youtube for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error starting the YouTube video selection. Please try again later.")
        return ConversationHandler.END


async def send_category_selection(update: Update):
    """
    Sends a message to the user with a list of categories to select from.
    """
    try:
        categories_text = "\n".join(CATEGORIES)
        message_text = f"Please select a topic from the following categories:\n{categories_text}"

        reply_keyboard = [[category] for category in CATEGORIES]
        await update.message.reply_text(
            message_text,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        app_logger.info(f"Sent category selection to user {update.effective_user.username} ({update.effective_user.id}).")
    except Exception as e:
        app_logger.error(f"Error in send_category_selection for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error displaying the category selection. Please try again later.")



async def get_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user's topic selection by validating the input and updating the user's data.

    Returns:
        int: The next state in the conversation flow, which can be either YOUTUBE_TOPIC or VIDEO_LENGTH.
    """
    try:
        selected_topic = update.message.text
        app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) selected topic: {selected_topic}")

        if selected_topic not in CATEGORIES:
            app_logger.warning(f"User {update.effective_user.username} selected an invalid topic: {selected_topic}")
            await send_invalid_topic_message(update)
            return YOUTUBE_TOPIC

        context.user_data['topic'] = selected_topic
        await update.message.reply_text("Please enter the video length (short, medium, long):")
        return VIDEO_LENGTH
    except Exception as e:
        app_logger.error(f"Error in get_topic for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error processing the selected topic. Please try again later.")
        return YOUTUBE_TOPIC


async def send_invalid_topic_message(update: Update):
    """
    Sends an invalid topic message to the user.

    Raises:
        Exception: If an error occurs while sending the invalid topic message.
    """
    try:
        await update.message.reply_text(
            f"'{update.message.text}' is not a valid topic. Please select a topic from the following categories:\n" + "\n".join(CATEGORIES)
        )
        app_logger.info(f"Sent invalid topic message to user {update.effective_user.username} ({update.effective_user.id}).")
    except Exception as e:
        app_logger.error(f"Error in send_invalid_topic_message for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error sending the invalid topic message. Please try again later.")



async def get_video_length(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Asynchronously handles the video length selection by the user in a conversation.

    Returns:
        int: The next state of the conversation. Which is VIDEO_LENGTH

    Raises:
        Exception: If there is an error processing the video length.

    This function retrieves the video length selected by the user from the message text. It then stores the video length in the user data of the conversation context. The function logs the selected video length and the topic associated with the user. If the video length is invalid, it sends an error message to the user and returns the VIDEO_LENGTH state. If the video length is valid, it calls the fetch_and_display_video_links function to fetch and display video links based on the topic and video length, and returns the ConversationHandler.END state. If there is an error processing the video length, it logs the error and sends an error message to the user.
    """
    try:
        video_length = update.message.text
        context.user_data['video_length'] = video_length
        topic = context.user_data.get('topic', "")
        user_id = update.message.from_user.id

        app_logger.info(f"User {update.effective_user.username} ({user_id}) selected video length: {video_length} for topic: {topic}")

        if not is_valid_video_length(video_length):
            app_logger.warning(f"User {update.effective_user.username} selected an invalid video length: {video_length}")
            await update.message.reply_text("Invalid length. Please enter 'short', 'medium', or 'long':")
            return VIDEO_LENGTH

        await fetch_and_display_video_links(update,user_id, topic, video_length)
        return ConversationHandler.END
    except Exception as e:
        app_logger.error(f"Error in get_video_length for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error processing the video length. Please try again later.")
        return VIDEO_LENGTH


async def mark_video_watched_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Asynchronously handles the video watch status update by the user in a conversation.

    Raises:
        Exception: If there is an error updating the video watch status.

    This function retrieves the video index and video URL from the query data and updates the video watch status in the user data. It logs the updated video watch status and the topic associated with the user. If there is an error updating the video watch status, it logs the error and sends an error message to the user.
    """
    try:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        topic = context.user_data.get('topic', "")
        video_length = context.user_data.get('video_length', "")

        original_text = query.message.text
        keyboard = query.message.reply_markup.inline_keyboard

        video_index = get_video_index(query.data)
        video_links = extract_video_links(original_text)
        video_url = video_links[video_index].strip()

        app_logger.info(f"User {query.from_user.username} ({user_id}) marked video as watched: {video_url}")

        if await handle_video_watched(query, video_url, keyboard[video_index][0].text, user_id):
            return

        await update_watch_history(user_id, topic, video_length, video_url)

        new_keyboard = create_new_keyboard(keyboard, video_index)
        await query.edit_message_text(text=original_text, reply_markup=InlineKeyboardMarkup(new_keyboard))
        app_logger.info(f"Updated video watch status for user {query.from_user.username} ({user_id}).")
    except Exception as e:
        app_logger.error(f"Error in mark_video_watched_callback for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error marking the video as watched. Please try again later.")