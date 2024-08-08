import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User, Chat, Bot
from dotenv import load_dotenv

from bot.handlers.basic_handlers import start  # Import the start handler from handlers.py

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

PUBLIC_IP = "8.8.8.8"  # Example public IP address for testing

@pytest.mark.asyncio
async def test_start():
    # Create a mock bot object
    bot = AsyncMock(spec=Bot)
    bot.send_message = AsyncMock()

    # Create a mock user, chat, and message
    user = User(id=123, first_name='test', is_bot=False, username='bit_mentor_bot')
    chat = Chat(id=123, type='private')
    message = Message(message_id=1, date=None, chat=chat, text="/start", from_user=user)

    # Associate the bot with the message
    message.set_bot(bot)

    # Create a mock update object
    update = Update(update_id=1, message=message)

    # Create a mock context object
    context = MagicMock()
    context.bot = bot

    # Call the start function
    await start(update, context, PUBLIC_IP)

    # Custom check for send_message call
    send_message_called = False
    for call in bot.send_message.await_args_list:
        call_args, call_kwargs = call
        if call_kwargs.get('chat_id') == 123 and call_kwargs.get('text') == f'Hello! This is your bot.\nPublic IP: {PUBLIC_IP}':
            send_message_called = True
            break

    assert send_message_called, "send_message(chat_id=123, text='Hello! This is your bot.\nPublic IP: {PUBLIC_IP}') await not found"

if __name__ == '__main__':
    pytest.main()
