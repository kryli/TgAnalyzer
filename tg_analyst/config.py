"""
Configuration file for Telegram API credentials and default settings.
Sensitive data is loaded securely from environment variables via .env file.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv


# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Telegram API ID (you get this from https://my.telegram.org)
API_ID: int = int(os.getenv("TELEGRAM_API_ID"))

# Telegram API Hash (you get this from https://my.telegram.org)
API_HASH: str = os.getenv("TELEGRAM_API_HASH")

# Name of the local session file for Telethon
# It stores your login so you don't need to enter a code every time
SESSION_NAME: str = os.getenv("SESSION_NAME")

# Target Telegram group/channel link to scrape messages from
TARGET_CHAT: str = os.getenv("TARGET_CHAT")
