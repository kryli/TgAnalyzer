from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

from tg_analyst.config import API_ID, API_HASH, SESSION_NAME, TARGET_CHAT
from tg_analyst.utils.json_loader import save_json

from datetime import datetime
import os
import logging

BASE_DIR = os.getenv(
    "TGA_OUTPUT_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
)


def download_messages(limit=1000) -> str:
    """
    Downloads messages from a Telegram chat using Telethon and saves them to a JSON file,
    including sender's name and username.

    Args:
        limit (int): The maximum number of messages to retrieve.

    Returns:
        str: Path to the saved JSON file.
    """
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    try:
        client.start()
    except SessionPasswordNeededError:
        logging.error("❌ Two-step verification password required for this session.")
        raise

    messages = []
    print(f"📥 Connecting to chat: {TARGET_CHAT} ...")

    try:
        for msg in client.iter_messages(TARGET_CHAT, limit=limit):
            if msg.text and isinstance(msg.text, str) and msg.text.strip():
                sender = msg.sender

                sender_username = None
                sender_name = None

                if sender:
                    sender_username = sender.username
                    sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()

                messages.append({
                    'id': msg.id,
                    'date': msg.date.isoformat() if msg.date else None,
                    'sender_id': msg.sender_id,
                    'sender_username': sender_username,
                    'sender_name': sender_name,
                    'text': msg.text.strip()
                })
    except Exception as e:
        logging.error(f"❌ Failed to download messages: {e}")
        raise

    if not messages:
        logging.warning("⚠️ No messages downloaded.")
        print("⚠️ No messages were retrieved from the chat.")
        return ""

    raw_dir = os.path.join(BASE_DIR, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    filename = f"latest_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    path = os.path.join(raw_dir, filename)

    save_json(messages, path)

    print(f"✅ Saved {len(messages)} messages to {path}")
    logging.info(f"✅ Downloaded and saved {len(messages)} messages to {path}")

    if len(messages) < limit:
        print(f"⚠️ Only {len(messages)} messages found (requested {limit})")
        logging.warning(f"⚠️ Only {len(messages)} messages found (requested {limit})")

    return path
