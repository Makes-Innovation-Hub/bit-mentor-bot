import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes

TOPIC, VIDEO_LENGTH = range(2)
CATEGORIES = ["MongoDB", "SQL", "Databases", "System Design", "Data Structures", "Algorithms", "Python"]


async def start_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    categories_text = "\n".join(CATEGORIES)
    message_text = f"Please select a topic from the following categories:\n{categories_text}"

    reply_keyboard = [[category] for category in CATEGORIES]
    await update.message.reply_text(
        f"{message_text}",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return TOPIC


async def get_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_topic = update.message.text
    if selected_topic not in CATEGORIES:
        await update.message.reply_text(
            f"'{selected_topic}' is not a valid topic. Please select a topic from the following categories:\n" + "\n".join(
                CATEGORIES))
        return TOPIC

    context.user_data['topic'] = selected_topic
    await update.message.reply_text("Please enter the video length (short, medium, long):")
    return VIDEO_LENGTH


async def get_video_length(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    video_length = update.message.text

    topic = context.user_data.get('topic', "")
    if not topic:
        await update.message.reply_text("Error: Topic is missing or empty.")
        return ConversationHandler.END

    if video_length not in ["short", "medium", "long"]:
        await update.message.reply_text("Invalid length. Please enter 'short', 'medium', or 'long':")
        return VIDEO_LENGTH  # Stay in VIDEO_LENGTH state to allow re-entry
    print(topic,video_length,)
    try:
        # user_id = update.message.from_user.id
        # response = requests.get(f"http://localhost:8000/youtube/a?user_id={user_id}&topic={topic}&video_length={video_length}")
        # response.raise_for_status()
        # video_links = response.json()
        video_links = [
            "https://www.youtube.com/watch?v=fake10",
            "https://www.youtube.com/watch?v=fake7",
            "https://www.youtube.com/watch?v=fake3",
            "https://www.youtube.com/watch?v=fake4",
            "https://www.youtube.com/watch?v=fake5"
        ]
        if not video_links:
            await update.message.reply_text("No videos found.")
            return ConversationHandler.END  # End the conversation if no videos are found'
        context.user_data['video_length'] = video_length

        keyboard = [
            [InlineKeyboardButton("Watch video 1", callback_data="watch_1")],
            [InlineKeyboardButton("Watch video 2", callback_data="watch_2")],
            [InlineKeyboardButton("Watch video 3", callback_data="watch_3")],
            [InlineKeyboardButton("Watch video 4", callback_data="watch_4")],
            [InlineKeyboardButton("Watch video 5", callback_data="watch_5")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        reply_text = "Here are the top YouTube videos:\n\n" + "\n".join(video_links)
        await update.message.reply_text(reply_text, reply_markup=reply_markup)

    except requests.HTTPError as e:
        await update.message.reply_text(f"Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

    return ConversationHandler.END  # End the conversation after processing


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = query.message.reply_markup.inline_keyboard
    user_id = query.from_user.id
    topic = context.user_data.get('topic', "")
    video_length = context.user_data.get('video_length', "")

    # Get the original message text (video links)
    original_text = query.message.text

    # Extract the video index from the callback data
    video_index = int(query.data.split("_")[1])  # Adjust for zero-based index

    # Get the corresponding video URL from the original message
    video_links = original_text.split("\n")[1:]  # Skip the "Here are the top YouTube videos:" line
    video_url = video_links[video_index]
    print(f"User {user_id} clicked on: {video_url}")
    payload = {
        "user_id": str(user_id),
        "topic": topic,
        "video_length": video_length,
        "video_url": video_url
    }
    response = requests.post(
        "http://localhost:8000/youtube/update_user_stats",
        json=payload
    )
    response.raise_for_status()

    # Create a new keyboard with updated button texts
    new_keyboard = []

    for i in range(len(keyboard)):
        if query.data == f'watch_{i + 1}':
            # Add the "Watched" button for the pressed button
            new_keyboard.append([InlineKeyboardButton("Watched", callback_data=f"watch_{i + 1}")])
        else:
            # Add the existing button
            new_keyboard.append([keyboard[i][0]])

    # Edit the message with the new keyboard and preserve the original text
    await query.edit_message_text(text=original_text, reply_markup=InlineKeyboardMarkup(new_keyboard))
