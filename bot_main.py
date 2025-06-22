import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# === Set base directory for environment and file references ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.environ["TGANALYST_BASE_DIR"] = BASE_DIR

# === Logging and directory setup ===
TG_BOT_DIR = os.path.join(BASE_DIR, "tg_bot")
logs_dir = os.path.join(TG_BOT_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

output_dir = os.path.join(TG_BOT_DIR, "data")
os.makedirs(output_dir, exist_ok=True)
os.environ["TGA_OUTPUT_DIR"] = output_dir                   

logging.basicConfig(
    filename=os.path.join(logs_dir, "bot.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# === Load environment variables ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN not found in .env file")

# === Initialize the bot and dispatcher with in-memory FSM storage ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === Import and register router ===
from tg_bot.handlers import router
dp.include_router(router)

# === Main entry point for launching the bot ===
async def main():
    logging.info("🤖 Starting Telegram bot (aiogram v3)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
