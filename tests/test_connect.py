# test_bot.py
import os
import pytest
from unittest.mock import patch, Mock, AsyncMock
from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.basic_handlers import connect


@pytest.mark.asyncio
async def test_connect():
    update = Mock()
    context = Mock()
    update.message.reply_text = AsyncMock()

    mock_data = {"message": "Hello, World!"}

    # Mock the requests.get method
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        await connect(update, context)

        update.message.reply_text.assert_called_once_with(mock_data["message"])
