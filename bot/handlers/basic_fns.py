import requests
import os
from telegram import Update
from telegram.ext import ContextTypes
from setting.config import *


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, public_ip: str) -> None:
    message = f"Hello! This is your bot.\nPublic IP: {public_ip}"
    await update.message.reply_text(message)


async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.get(f"{config.SERVER_URL}/")
        response.raise_for_status()
        data = response.json()
        await update.message.reply_text(data["message"])
    except requests.RequestException as e:
        await update.message.reply_text(f"Error fetching data: {e}")
