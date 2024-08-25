import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from bot.config.logging_config import app_logger

def get_video_length_keyboard():
    button1 = KeyboardButton("short")
    button2 = KeyboardButton("medium")
    button3 = KeyboardButton("long")
    return ReplyKeyboardMarkup([[button1, button2, button3]], resize_keyboard=True, one_time_keyboard=True)

async def handle_video_watched(query: Update.callback_query, video_url: str, button_text: str, user_id: int) -> bool:
    """
    Handles the video watch status update by the user in a conversation.

    Args:
        query (Update.callback_query): The callback query object containing the user's interaction.
        video_url (str): The URL of the video being watched.
        button_text (str): The text on the button that was clicked.
        user_id (int): The ID of the user who interacted with the video.

    Returns:
        bool: True if the user has already watched the video, False otherwise.
    """
    if button_text == "Watched":
        print(f"User {user_id} clicked on 'Watched' for: {video_url}")
        await query.message.reply_text("You have already watched this video.")
        return True

    print(f"User {user_id} clicked on: {video_url}")
    await query.message.reply_text(f"You clicked on the video: {video_url}")
    return False

async def update_watch_history(user_id: int, topic: str, video_length: str, video_url: str):
    """
    Asynchronously updates the watch history for a given user.

    Args:
        user_id (int): The ID of the user whose watch history is being updated.
        topic (str): The topic associated with the video being watched.
        video_length (str): The length of the video being watched.
        video_url (str): The URL of the video being watched.

    Returns:
        None
    """
    try:
        payload = {
            "user_id": str(user_id),
            "topic": topic,
            "length": video_length,
            "video_url": video_url
        }

        app_logger.info(f"Updating watch history for user {user_id} with payload: {payload}")

        response = requests.post(
            "http://localhost:8000/youtube/mark_link_watched",
            json=payload
        )
        response.raise_for_status()
        app_logger.info(f"Successfully updated watch history for user {user_id}")
    except requests.HTTPError as e:
        app_logger.error(f"HTTP error while updating watch history for user {user_id}: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        app_logger.error(f"Unexpected error while updating watch history for user {user_id}: {str(e)}")


def create_new_keyboard(keyboard: list, video_index: int) -> list:
    """
    Creates a new keyboard with a "Watched" button at the specified index.

    Args:
        keyboard (list): The original keyboard.
        video_index (int): The index at which the "Watched" button should be added.

    Returns:
        list: The new keyboard with the "Watched" button.

    Raises:
        Exception: If an error occurs while creating the new keyboard.
    """
    try:
        new_keyboard = []
        for i in range(len(keyboard)):
            if i == video_index:
                new_keyboard.append([InlineKeyboardButton("Watched", callback_data=f"watch_{i + 1}")])
            else:
                new_keyboard.append([keyboard[i][0]])
        app_logger.info(f"Created new keyboard with 'Watched' button at index {video_index}")
        return new_keyboard
    except Exception as e:
        app_logger.error(f"Error creating new keyboard: {str(e)}")
        return keyboard  # Return the original keyboard if something goes wrong

def extract_video_links(original_text: str) -> list:
    """
    Extracts YouTube video links from a given text.

    Args:
        original_text (str): The text containing the video links.

    Returns:
        list: A list of extracted video links.

    Raises:
        Exception: If an error occurs during the extraction process.
    """
    try:
        video_links = original_text.split("\n")[2:]
        app_logger.info(f"Extracted video links: {video_links}")
        return video_links
    except Exception as e:
        app_logger.error(f"Error extracting video links: {str(e)}")
        return []

def get_video_index(callback_data: str) -> int:
    """
    Extracts the video index from the provided callback data.

    Args:
        callback_data (str): The callback data containing the video index.

    Returns:
        int: The extracted video index. Returns -1 if an error occurs.
    """
    try:
        index = int(callback_data.split("_")[1]) - 1
        app_logger.info(f"Extracted video index: {index}")
        return index
    except Exception as e:
        app_logger.error(f"Error getting video index from callback data: {str(e)}")
        return -1  # Return an invalid index if something goes wrong

def is_valid_video_length(video_length: str) -> bool:
    """
    Checks if a given video length is valid.

    Args:
        video_length (str): The length of the video to check.

    Returns:
        bool: True if the video length is valid, False otherwise.
    """
    valid_lengths = ["short", "medium", "long"]
    if video_length in valid_lengths:
        app_logger.info(f"Video length '{video_length}' is valid")
        return True
    else:
        app_logger.warning(f"Invalid video length: {video_length}")
        return False

async def display_video_links(update, video_links: list):
    """
    Displays a list of YouTube video links to the user.

    Args:
        update: The incoming update object.
        video_links (list): A list of YouTube video links to display.
    """
    try:
        keyboard = [
            [InlineKeyboardButton(f"Watch video {i + 1}", callback_data=f"watch_{i + 1}")]
            for i in range(len(video_links))
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        reply_text = "Here are the top YouTube videos:\n\n" + "\n".join(video_links)
        await update.message.reply_text(reply_text, reply_markup=reply_markup)
        app_logger.info("Displayed video links to the user")
    except Exception as e:
        app_logger.error(f"Error displaying video links: {str(e)}")
        await update.message.reply_text("An error occurred while displaying video links. Please try again later.")

async def fetch_and_display_video_links(update: Update,user_id, topic: str, video_length: str):
    """
    Fetches YouTube video links based on the provided topic and video length, 
    and displays them to the user.

    Args:
        update (Update): The incoming update object.
        user_id: The ID of the user requesting the video links.
        topic (str): The topic for which to fetch video links.
        video_length (str): The length of the videos to fetch.
    """
    try:
        app_logger.info(f"Fetching video links for topic '{topic}' with length '{video_length}'")
        payload={
                "topic": topic,
                "length": video_length,
                "user_id": str(user_id)
            }
        # Uncomment to make an actual API request
        response = requests.post(
            "http://localhost:8000/youtube/",
            json=payload
        )
        response.raise_for_status()
        video_links = response.json()

        # Sample video links for testing
        # video_links = [
        #     "https://www.youtube.com/watch?v=fake10",
        #     "https://www.youtube.com/watch?v=fake7",
        #     "https://www.youtube.com/watch?v=fake3",
        #     "https://www.youtube.com/watch?v=fake4",
        #     "https://www.youtube.com/watch?v=fake5"
        # ]

        if not video_links:
            await update.message.reply_text("No videos found.")
            app_logger.info("No videos found for the given criteria.")
            return

        await display_video_links(update, video_links)

    except requests.HTTPError as e:
        app_logger.error(f"HTTP error while fetching video links: {e.response.status_code} - {e.response.text}")
        await update.message.reply_text(f"Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        app_logger.error(f"Unexpected error while fetching video links: {str(e)}")
        await update.message.reply_text(f"An error occurred: {str(e)}")