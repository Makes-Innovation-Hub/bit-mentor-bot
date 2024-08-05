## YOUTUBE API:
### Instructions for Setting Up and Running the Bot
1.  **Get the YouTube API Key:**
	* Obtain the API key from the Google Developer Console. You will need this key to make requests to the YouTube Data API
2. **Set Up Environment Variables in SERVER:**
	*	Add your YouTube API key to the `.env_dev` file:
	```python
	YOUTUBE_API_DEV = your_youtube_api_key
	```
	or Add your YouTube API key to the `.env_prod` file:
	```python
	 YOUTUBE_API_PROD = your_youtube_api_key
	```
3.  **Run the Server:**
4.  **Run the Bot:**

5. **Use the Bot:**
	-   Open Telegram and start the bot.
	-   Type `/youtube`.
	-   Enter the topic when prompted.
	-   Enter the video length (short, medium, or long) when prompted.
	-   The bot will return a list of YouTube video links based on the provided topic and video length.
---
### Flow Overview
* UI > Bot > Server > Bot > UI
---
### Handling Overflow Scenarios

-   **YouTube Data API Quota Limit**: If you exceed your daily quota limit (10,000 units per day) for the YouTube Data API, the bot will not be able to fetch video links.
You can see your quota usage on the [Quotas](https://console.developers.google.com/iam-admin/quotas?pli=1&project=google.com:api-project-314373636293&folder=&organizationId=) page in the API Console.

---
## Technical Details:
**Packages Used**:

-   `requests`: Used for making HTTP requests to the backend server's `/youtube/` endpoint.

-   `telegram`: Part of the `python-telegram-bot` library, used for interacting with the Telegram Bot API.
-   `telegram.ext`: An extension of the `telegram` package, providing higher-level classes and functions for managing conversation flow and handling user inputs. such as: ConversationHandler,CommandHandler,MessageHandler...
- `googleapiclient` is a Python library that provides a simple and consistent way to interact with Google APIs. It allows developers to easily build and manage requests to various Google services, such as YouTube...
### Connecting to the YouTube API
```python

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from setting.config import config
def connect_to_youtube_api():
    try:
        youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API)
        return youtube
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None
```
-   **`build`**: Creates a resource object for interacting with the YouTube Data API.
-   **`config.YOUTUBE_API`**: Refers to the YouTube API key that you've set up in your configuration.
-   The `connect_to_youtube_api` function handles connection errors and returns the YouTube service object if the connection is successful.