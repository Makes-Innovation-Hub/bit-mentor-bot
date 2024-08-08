import pytest
from unittest.mock import AsyncMock, patch

import requests
from telegram import Update, Message
from telegram.ext import ContextTypes

from bot.handlers.youtube_handler import get_video_length


@pytest.mark.asyncio
async def test_get_video_length_success():
    # Setup Mocks
    update = AsyncMock(Update)
    context = AsyncMock(ContextTypes.DEFAULT_TYPE)
    message = AsyncMock(Message)
    update.message = message

    context.user_data = {'topic': 'Python programming'}
    update.message.text = "short"

    # Mock the requests.get to simulate a successful API response
    with patch('bot.handlers.youtube_handler.requests.get') as mocked_get:  # Adjust the patch target as needed
        mocked_get.return_value.json.return_value = ["link1", "link2", "link3", "link4", "link5"]
        mocked_get.return_value.status_code = 200

        # Run the function
        await get_video_length(update, context)

        reply_text = "Here are the top YouTube videos:\n\nlink1\nlink2\nlink3\nlink4\nlink5"
        update.message.reply_text.assert_called_once_with(reply_text)


@pytest.mark.asyncio
async def test_get_video_length_failure_topic_missing():
    # Setup Mocks
    update = AsyncMock(Update)
    context = AsyncMock(ContextTypes.DEFAULT_TYPE)
    message = AsyncMock(Message)
    update.message = message

    context.user_data = {}  # Topic is missing
    update.message.text = "short"

    # Run the function
    await get_video_length(update, context)

    error_text = "Error: 400 - {\"detail\":\"Topic cannot be an empty string\"}"
    update.message.reply_text.assert_called_once_with(error_text)


@pytest.mark.asyncio
async def test_get_video_length_failure_invalid_length():
    # Setup Mocks
    update = AsyncMock(Update)
    context = AsyncMock(ContextTypes.DEFAULT_TYPE)
    message = AsyncMock(Message)
    update.message = message

    context.user_data = {'topic': 'Python programming'}
    update.message.text = "aaaaaaaaaaaaa"  # Invalid length

    # Run the function
    await get_video_length(update, context)

    # Assertions
    error_text = "Invalid length. Please enter 'short', 'medium', or 'long':"
    update.message.reply_text.assert_called_once_with(error_text)


@pytest.mark.asyncio
async def test_get_video_length_connection_failure():
    # Setup Mocks
    update = AsyncMock(Update)
    context = AsyncMock(ContextTypes.DEFAULT_TYPE)
    message = AsyncMock(Message)
    update.message = message

    context.user_data = {'topic': 'Python programming'}
    update.message.text = "short"

    # Mock the requests.get to simulate a connection failure
    with patch('bot.handlers.youtube_handler.requests.get') as mocked_get:
        mocked_get.side_effect = requests.ConnectionError("Failed to connect to YouTube API")

        # Run the function
        await get_video_length(update, context)

        # Assertions
        error_text = "An error occurred: Failed to connect to YouTube API"
        update.message.reply_text.assert_called_once_with(error_text)
