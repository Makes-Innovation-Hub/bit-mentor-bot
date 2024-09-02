# tests/test_env.py
import os
from dotenv import load_dotenv
import pytest
import logging

load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_bot_token():
    bot_token = os.getenv("BOT_TOKEN_DEV")
    logger.debug(f"BOT_TOKEN: {bot_token}")
    assert bot_token is not None, "BOT_TOKEN environment variable is not set"
