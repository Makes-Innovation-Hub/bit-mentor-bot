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
        app_logger.info(
            f"User {update.effective_user.username} ({update.effective_user.id}) started YouTube video selection.")
        await send_category_selection(update)
        return YOUTUBE_TOPIC
    except Exception as e:
        app_logger.error(
            f"Error in start_youtube for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text(
            "There was an error starting the YouTube video selection. Please try again later.")
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
        app_logger.info(
            f"Sent category selection to user {update.effective_user.username} ({update.effective_user.id}).")
    except Exception as e:
        app_logger.error(
            f"Error in send_category_selection for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error displaying the category selection. Please try again later.")


async def get_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user's topic selection by validating the input and updating the user's data.

    Returns:
        int: The next state in the conversation flow, which can be either YOUTUBE_TOPIC or VIDEO_LENGTH.
    """
    try:
        selected_topic = update.message.text
        app_logger.info(
            f"User {update.effective_user.username} ({update.effective_user.id}) selected topic: {selected_topic}")

        if selected_topic not in CATEGORIES:
            app_logger.warning(f"User {update.effective_user.username} selected an invalid topic: {selected_topic}")
            await send_invalid_topic_message(update)
            return YOUTUBE_TOPIC

        context.user_data['topic'] = selected_topic
        await update.message.reply_text("Please enter the video length (short, medium, long):")
        return VIDEO_LENGTH
    except Exception as e:
        app_logger.error(
            f"Error in get_topic for user {update.effective_user.username} ({update.effective_user.id}): {e}")
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
            f"'{update.message.text}' is not a valid topic. Please select a topic from the following categories:\n" + "\n".join(
                CATEGORIES)
        )
        app_logger.info(
            f"Sent invalid topic message to user {update.effective_user.username} ({update.effective_user.id}).")
    except Exception as e:
        app_logger.error(
            f"Error in send_invalid_topic_message for user {update.effective_user.username} ({update.effective_user.id}): {e}")
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

        app_logger.info(
            f"User {update.effective_user.username} ({user_id}) selected video length: {video_length} for topic: {topic}")

        if not is_valid_video_length(video_length):
            app_logger.warning(
                f"User {update.effective_user.username} selected an invalid video length: {video_length}")
            await update.message.reply_text("Invalid length. Please enter 'short', 'medium', or 'long':")
            return VIDEO_LENGTH

        await fetch_and_display_video_links(update,context ,user_id, topic, video_length)
        return ConversationHandler.END
    except Exception as e:
        app_logger.error(
            f"Error in get_video_length for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error processing the video length. Please try again later.")
        return VIDEO_LENGTH


async def mark_video_watched_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Asynchronously handles the video watch status update by the user in a conversation.

    Raises:
        Exception: If there is an error updating the video watch status.
    """
    try:
        # Get the callback query from the update
        query = update.callback_query
        await query.answer()

        # Retrieve user ID, topic, and video length from user data
        user_id = query.from_user.id
        topic = context.user_data.get('topic', '')
        video_length = context.user_data.get('video_length', '')

        # Extract video index from the callback data
        video_index_str = query.data
        try:
            video_index = int(video_index_str.replace('watch_', ''))
        except ValueError:
            app_logger.warning(f"Invalid callback data format: {video_index_str}")
            await query.message.reply_text("Invalid selection. Please try again.")
            return

        # Retrieve video URLs and titles from user data
        video_urls = context.user_data.get('video_urls', [])
        video_titles = context.user_data.get('video_titles', [])

        # Check if the video_index is within bounds
        if not video_urls or not video_titles or video_index < 0 or video_index >= len(video_urls):
            app_logger.warning(f"Video index out of range or missing data: {video_index}")
            await query.message.reply_text("Video URL or title not found. Please try again later.")
            return

        # Get the video URL and title
        video_url = video_urls[video_index]
        video_title = video_titles[video_index]

        # Handle the video watch status
        button_text = query.message.reply_markup.inline_keyboard[video_index][0].text
        is_watched = await handle_video_watched(query, video_url, button_text, user_id)

        if not is_watched:
            # Update watch history
            await update_watch_history(user_id, topic, video_length, video_url)

            # Update the keyboard
            message = query.message
            original_text = message.text
            keyboard = message.reply_markup.inline_keyboard
            new_keyboard = create_new_keyboard(keyboard, video_index)

            # Update the message text and keyboard
            new_message_text = original_text + "\n\nVideo marked as watched."
            await query.edit_message_text(text=new_message_text, reply_markup=InlineKeyboardMarkup(new_keyboard))

            app_logger.info(f"Updated video watch status for user {query.from_user.username} ({user_id}).")
    except Exception as e:
        app_logger.error(
            f"Error in mark_video_watched_callback for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await query.message.reply_text("There was an error marking the video as watched. Please try again later.")
