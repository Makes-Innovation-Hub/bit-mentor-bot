import requests
from telegram import Update
from telegram.ext import  ConversationHandler, ContextTypes


TOPIC, VIDEO_LENGTH = range(2)


async def start_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please enter the topic:")
    return TOPIC  # Return TOPIC state


async def get_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['topic'] = update.message.text  # Save the topic
    await update.message.reply_text("Please enter the video length (short, medium, long):")
    return VIDEO_LENGTH  # Return VIDEO_LENGTH state


async def get_video_length(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    video_length = update.message.text

    topic = context.user_data.get('topic', "")
    if not topic:
        await update.message.reply_text("Error: Topic is missing or empty.")
        return ConversationHandler.END

    if video_length not in ["short", "medium", "long"]:
        await update.message.reply_text("Invalid length. Please enter 'short', 'medium', or 'long':")
        return VIDEO_LENGTH  # Stay in VIDEO_LENGTH state to allow re-entry

    topic = context.user_data['topic']
    try:
        response = requests.get(f"http://localhost:8000/youtube/?topic={topic}&video_length={video_length}")
        response.raise_for_status()
        video_links = response.json()

        if not video_links:
            await update.message.reply_text("No videos found.")
            return ConversationHandler.END  # End the conversation if no videos are found

        reply_text = "Here are the top YouTube videos:\n\n" + "\n".join(video_links)
        await update.message.reply_text(reply_text)

    except requests.HTTPError as e:
        await update.message.reply_text(f"Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

    return ConversationHandler.END  # End the conversation after processing

