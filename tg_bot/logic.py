import logging
import os
import sys
from datetime import datetime
from telethon.sync import TelegramClient
from telethon import TelegramClient as AsyncTelegramClient
from tg_analyst.config import API_ID, API_HASH, SESSION_NAME
from tg_analyst.utils.json_loader import save_json

BASE_DIR = os.environ.get("TGANALYST_BASE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(BASE_DIR)

from tg_bot.run_analytics import run_analysis_from_group


async def process_chat_analysis(url: str) -> str:
    """
    Joins the Telegram group, downloads messages, and runs the analysis pipeline.
    
    Args:
        url (str): Link or @username of the Telegram group/channel
    
    Returns:
        str: Path to the final GPT report file, or None if failed.
    """
    logging.info(f"🚀 Starting chat analysis for: {url}")

    try:
        client = AsyncTelegramClient(SESSION_NAME, API_ID, API_HASH)
        await client.start()
        entity = await client.get_entity(url)

        messages = []
        async for msg in client.iter_messages(entity, limit=500):
            if msg.text and msg.sender_id:
                sender = await msg.get_sender()
                sender_username = getattr(sender, "username", None)
                first = getattr(sender, 'first_name', '') or ''
                last = getattr(sender, 'last_name', '') or ''

                first = first.strip()
                last = last.strip()

                if first.lower() == 'none':
                    first = ''
                if last.lower() == 'none':
                    last = ''

                sender_name = f"{first} {last}".strip() or "Unknown"

                messages.append({
                    "id": msg.id,
                    "date": msg.date.isoformat() if msg.date else None,
                    "sender_id": msg.sender_id,
                    "sender_username": sender_username,
                    "sender_name": sender_name,
                    "text": msg.text.strip()
                })

        # Save messages
        raw_dir = os.path.join(BASE_DIR, "tg_bot", "data", "raw")
        os.makedirs(raw_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(raw_dir, f"chat_{timestamp}.json")
        save_json(messages, json_path)
        logging.info(f"✅ Saved {len(messages)} messages to {json_path}")

        # Run analysis
        run_analysis_from_group(json_path)

        final_path = os.path.join(BASE_DIR, "tg_bot", "data", "results", "final_analysis_gpt.txt")
        if os.path.exists(final_path):
            logging.info(f"📄 Final report found at {final_path}")
            return final_path
        else:
            logging.warning("⚠️ Analysis completed but final report not found.")
            return None

    except Exception as e:
        logging.exception("❌ Failed to process chat:")
        return None
