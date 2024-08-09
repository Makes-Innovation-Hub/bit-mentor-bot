import requests
import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.config.logging_config import logger
from bot.setting.config import config

# Bot commands
difficulty_button1 = KeyboardButton("easy")
difficulty_button2 = KeyboardButton("medium")
difficulty_button3 = KeyboardButton("hard")
difficulty_button4 = KeyboardButton("none")
difficulty_keyboard = ReplyKeyboardMarkup([[difficulty_button1, difficulty_button2, difficulty_button3, difficulty_button4]],
                               resize_keyboard=True, one_time_keyboard=True)

answers_button1 = KeyboardButton("1")
answers_button2 = KeyboardButton("2")
answers_button3 = KeyboardButton("3")
answers_button4 = KeyboardButton("4")
answers_keyboard = ReplyKeyboardMarkup([[answers_button1, answers_button2], [answers_button3, answers_button4]], resize_keyboard=True, one_time_keyboard=True)

DIFFICULTY, ANSWERS, TOPIC, USER_ANSWER = range(4)

# Suppress unnecessary debug logs
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, public_ip: str) -> None:
    logger.info(f"Start command received from user: {update.effective_user.username}")
    logger.info(f"Public IP: {public_ip} will be used in the start message")
    message = f"Hello! This is your bot.\nPublic IP: {public_ip}"
    logger.info(f"Sending start message: {message}")
    await update.message.reply_text(message)
    logger.info("Start message sent successfully")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Help command received from user: {update.effective_user.username}")
    help_message = (
        "To get a question you need to use /question\n"
        "You will be asked to enter the required information\n"
        "First you need to enter a difficulty\n"
        "Then enter the number of answers\n"
        "Then enter the topic"
    )
    logger.info("Prepared help message")
    logger.info(f"Sending help message: {help_message}")
    await update.message.reply_text(help_message)
    logger.info("Help message sent successfully")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"Cancel command received from user: {update.effective_user.username}")
    logger.info("Canceling the ongoing operation")
    await update.message.reply_text("Operation canceled.")
    logger.info("Cancellation message sent successfully")
    return ConversationHandler.END

async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Connect command received from user: {update.effective_user.username}")
    try:
        logger.info(f"Attempting to connect to server at {config.SERVER_URL}")
        response = requests.get(f"{config.SERVER_URL}/")
        logger.info(f"Request made to server, status code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        logger.info(f"Server response: {data['message']}")
        await update.message.reply_text(data["message"])
        logger.info("Server response message sent successfully")
    except requests.RequestException as e:
        logger.error(f"Error fetching data from server: {e}")
        await update.message.reply_text(f"Error fetching data: {e}")
        logger.info("Error message sent to user")

