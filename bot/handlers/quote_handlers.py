from telegram import Update
from telegram.ext import ContextTypes
import requests
from bot.setting.config import config
from bot.config.logging_config import app_logger
from bot.utils.jwt_utils import create_jwt

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the quote command by fetching a random quote from the server and sending it back to the user.
    
    """
    user_id = update.message.from_user.id
    app_logger.info(f"User {update.effective_user.username} ({user_id}) triggered quote command")

    try:
        token = create_jwt(user_id)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(f"{config.SERVER_URL}/quote/{user_id}", headers=headers)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        data = response.json()
        # Extract the quote and author from the response
        quote = data.get("quote")
        author = data.get("author")
        # Send the quote back to the user
        if quote and author:
            reply = f'"{quote}" - {author}'
            app_logger.info(f"Quote retrieved successfully for user {user_id}: {quote} - {author}")
            await update.message.reply_text(reply)
        else:
            app_logger.warning(f"Incomplete quote data received for user {user_id}: {data}")
            await update.message.reply_text("Received incomplete quote data. Please try again later.")

    except requests.RequestException as e:
        app_logger.error(f"Request error when fetching quote for user {user_id}: {e}")
        await update.message.reply_text("Error when fetching quote. Please try again later.")

    except Exception as e:
        app_logger.error(f"Unexpected error in quote_command for user {user_id}: {e}")
        await update.message.reply_text("An unexpected error occurred. Please try again later.")
