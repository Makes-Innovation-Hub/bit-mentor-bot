import os
import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import pytz
from constants import SCOPES 
from bot.utils.task_utils import get_timezone, is_valid_datetime
from bot.setting.config import config
from bot.config.logging_config import app_logger

TITLE, START, END, LOCATION, CODE = range(5)
async def task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    This function initiates a task conversation by asking the user for the task title.
    
    Returns:
        int: The TITLE constant, indicating the next state in the conversation.
    """
    try:
        context.user_data["operation"] = "task command"
        app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) triggered task command")
        await update.message.reply_text("What is the title of your task? (or /cancel to cancel this conversation)")
        app_logger.info("Sent title prompt to user")
        return TITLE
    except Exception as e:
        app_logger.error(f"Error in task command: {e}")
        await update.message.reply_text("There was an error starting the task process. Please try again.")
        return ConversationHandler.END


    

async def title_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    This function handles the title response in a task conversation.
    
    It saves the title of the task in the user's data and prompts the user to enter the start date of the task.
    
    Returns:
        int: The START constant, indicating the next state in the conversation.
    """
    try:
        app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) given title {update.message.text} in task command")

        context.user_data['title'] = update.message.text
        await update.message.reply_text("Enter the start date of your task? (YYYY-MM-DD HH:MM:SS) (or /cancel to cancel this conversation)")
        app_logger.info("Sent start date prompt to user")

        return START
    except Exception as e:
        app_logger.error(f"Error in title_response: {e}")
        await update.message.reply_text("There was an error starting the task process. Please try again.")
        return TITLE

async def start_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    This function handles the start date response in a task conversation.
    
    It checks if the provided date is valid, and if so, saves it in the user's data and prompts the user to enter the end date of the task.
    
    Returns:
        int: The END constant if the date is valid, indicating the next state in the conversation. Otherwise, the START constant.
    """
    try:
        app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) given start date {update.message.text} in task command")
        if is_valid_datetime(update.message.text):
            context.user_data['start'] = update.message.text
            await update.message.reply_text("Enter the end date of your task? (YYYY-MM-DD HH:MM:SS) (or /cancel to cancel this conversation)")
            app_logger.info("Sent end date prompt to user")
            return END
        else:
            await update.message.reply_text("Invalid date format. Please enter a valid date in the format YYYY-MM-DD HH:MM:SS.")
            app_logger.info("User sent invalid date format in task command")
            return START
    except Exception as e:
        app_logger.error(f"Error in start_response: {e}")
        await update.message.reply_text("There was an error starting the task process. Please try again.")
        return START

async def end_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    This function handles the end date response in a task conversation.
    
    It checks if the provided date is valid, and if so, saves it in the user's data and prompts the user to share their location for timezone information.
    
    Returns:
        int: The LOCATION constant if the date is valid, indicating the next state in the conversation. Otherwise, the END constant.
    """
    try:
        app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) given end date {update.message.text} in task command")

        if is_valid_datetime(update.message.text):
            context.user_data['end'] = update.message.text
            await update.message.reply_text(
            'Please share your location for timezone information. (or /cancel to cancel this conversation)' ,
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Share Location", request_location=True)]], one_time_keyboard=True)
            )
            app_logger.info("Sent location prompt to user")

            return LOCATION
        else:
            await update.message.reply_text("Invalid date format. Please enter a valid date in the format YYYY-MM-DD HH:MM:SS.")
            app_logger.info("User sent invalid date format in task command")
            return END
    except Exception as e:
        app_logger.error(f"Error in end_response: {e}")
        await update.message.reply_text("There was an error starting the task process. Please try again.")
        return END

async def location_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    This function handles the location response in a task conversation.
    
    It checks if the provided location is valid, and if so, saves it in the user's data, 
    determines the timezone, and prompts the user to authorize the application.
    
    Returns:
        int: The CODE constant, indicating the next state in the conversation.
    """
    try:
        app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) given location {update.message.text} in task command")
        if update.message.location is None:
            await update.message.reply_text("Please share your location for timezone information:")
            return LOCATION
        user_location = update.message.location
        context.user_data['location'] = (user_location.latitude, user_location.longitude)
        timezone_str = get_timezone(context.user_data['location'])
        # get the start and end dates
        start_date_str = context.user_data['start']
        end_date_str = context.user_data['end']
        # format the dates
        dt_start = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        dt_end = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
        # get user timezone based on location
        timezone = pytz.timezone(timezone_str)
        dt_start = timezone.localize(dt_start)
        dt_end = timezone.localize(dt_end)
        # get the OAuth credentials for the Google Calendar API
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_DEV")

        credentials_dict = json.loads(credentials_json)
        
        flow = InstalledAppFlow.from_client_config(
            credentials_dict, SCOPES
        )
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        context.user_data['flow'] = flow
        context.user_data['dt_start'] = dt_start
        context.user_data['dt_end'] = dt_end
        context.user_data['timezone_str'] = timezone_str

        await update.message.reply_text(
            "Please visit the following URL to authorize this application and provide the authorazation code here:\n" + auth_url
        )
        app_logger.info("Sent auth code  prompt to user")
        return CODE
    except Exception as e:
        app_logger.error(f"Error in location_response: {e}")
        await update.message.reply_text("There was an error starting the task process. Please try again.")
        return LOCATION

async def auth_code_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    This function handles the authorization code response in a task conversation.
    
    It fetches the token using the provided authorization code, creates a Google Calendar API service,
    and inserts a new event into the primary calendar.

    Returns:
        int: The ConversationHandler.END constant, indicating the end of the conversation.
    """
    try:
        app_logger.info(f"User {update.effective_user.username} ({update.effective_user.id}) given auth code {update.message.text} in task command")
        flow = context.user_data['flow']
        dt_start = context.user_data['dt_start']
        dt_end = context.user_data['dt_end']
        timezone_str = context.user_data['timezone_str']
        code = update.message.text

        try:
            flow.fetch_token(code=code)
            creds = flow.credentials

            service = build("calendar", "v3", credentials=creds)
            # create the event
            event = {
                'summary': context.user_data['title'],
                'start': {
                    'dateTime': dt_start.isoformat(),
                    'timeZone': timezone_str,
                },
                'end': {
                    'dateTime': dt_end.isoformat(),
                    'timeZone': timezone_str,
                }
            }

            event = service.events().insert(calendarId='primary', body=event).execute()
            await update.message.reply_text(f"Event created: {event.get('htmlLink')}")
            app_logger.info("Sent event to user")

        except Exception as e:
            await update.message.reply_text(f"Failed to create event: {str(e)}")
            app_logger.info("Sent event failed to user")

        return ConversationHandler.END
    except Exception as e:
        app_logger.error(f"Error in auth_code_response: {e}")
        await update.message.reply_text("There was an error starting the task process. Please try again.")
        return CODE
