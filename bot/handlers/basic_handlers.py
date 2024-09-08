import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from bot.config.logging_config import app_logger
from bot.setting.config import config
from bot.utils.jwt_utils import create_jwt

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, public_ip: str) -> None:
    """
    Sends a welcome message to the user with their public IP address.

    Args:
        public_ip (str): The public IP address of the user.
    """
    message = f"Hello! This is your bot.\nPublic IP: {public_ip}"
    app_logger.info(message)
    await update.message.reply_text(message)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the help command by sending a message to the user with a list of available commands.
    """
    app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) triggered help command.")
    await update.message.reply_text(
        "/question - Get a random question\n"
        "/quote - Get a random motivational quote\n"
        "/task - Set a task in your google calendar\n"
        "/youtube - Get a youtube video\n"
        "/cancel - Cancel the current conversation\n"
        "for some of these command you will be asked to enter some data, follow the instructions in the message")

    app_logger.info("Help message sent successfully")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the cancel command by canceling the current operation and sending a confirmation message to the user.

    Returns:
        int: The ConversationHandler.END state, indicating the end of the conversation.
    """
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username
        app_logger.info(f"User {username} ({user_id}) triggered cancel command.")

        # Determine what operation was canceled
        if 'operation' in context.user_data:
            operation = context.user_data.pop('operation')
            message = f"The operation '{operation}' has been canceled."
            app_logger.info(f"User {username} ({user_id}) canceled the operation: {operation}")
        else:
            message = "There was no active operation to cancel."
            app_logger.info(f"User {username} ({user_id}) attempted to cancel, but no operation was active.")

        await update.message.reply_text(message)
    except Exception as e:
        app_logger.error(f"Error during cancellation for user {username} ({user_id}): {e}")
        await update.message.reply_text("An error occurred while attempting to cancel the operation. Please try again later.")

    return ConversationHandler.END


async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the connect command by sending a GET request to the server and sending the response message back to the user.
    """
    try:
        app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) triggered connect command.")

        token = create_jwt(update.effective_user.id)
        headers = {
        'Authorization': f'Bearer {token}',
        }
        
        response = requests.get(f"{config.SERVER_URL}/", headers=headers)
        response.raise_for_status()
        data = response.json()
        app_logger.info("Connection successful, sending response message")
        await update.message.reply_text(data["message"])
    except requests.RequestException as e:
        app_logger.error(f"Error fetching data for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text(f"Error fetching data: {e}")