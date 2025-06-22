import os
import sys
import logging
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode

BASE_DIR = os.environ.get("TGANALYST_BASE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(BASE_DIR)

from tg_bot.logic import process_chat_analysis
from tg_bot.utils.formatting import format_report_md



router = Router()

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📊 User Activity"),
            KeyboardButton(text="📝 Message Activity"),
            KeyboardButton(text="🔄 Restart Analysis"),
        ]
    ],
    resize_keyboard=True
)

user_states = {}

# Cache for storing results keyed by chat URL
analysis_cache = {}

# Fake analysis function for testing — returns existing report path without real analysis
async def fake_process_chat_analysis(url: str) -> str:
    base_results = os.path.join(BASE_DIR, "tg_bot", "data", "results")
    return os.path.join(base_results, "final_analysis_gpt.txt")


@router.message()
async def universal_handler(message: Message):
    text = message.text.strip()
    logging.info(f"Received message: {text!r} from user {message.from_user.id}")

    if text in ["📊 User Activity", "📝 Message Activity", "🔄 Restart Analysis"]:
        state = user_states.get(message.from_user.id)
        logging.info(f"User state for buttons: {state}")

        if not state or state.get("status") != "ready":
            await message.answer("Please send me a Telegram chat/group link to analyze first.")
            return

        if text == "📊 User Activity":
            photo_path = state.get("user_activity_path")
            logging.info(f"Sending user activity graph from: {photo_path}")
            if photo_path and os.path.exists(photo_path):
                await message.answer_photo(photo=FSInputFile(photo_path))
            else:
                await message.answer("⚠️ User activity graph not found.")

        elif text == "📝 Message Activity":
            photo_path = state.get("message_activity_path")
            logging.info(f"Sending message activity graph from: {photo_path}")
            if photo_path and os.path.exists(photo_path):
                await message.answer_photo(photo=FSInputFile(photo_path))
            else:
                await message.answer("⚠️ Message activity graph not found.")

        elif text == "🔄 Restart Analysis":
            logging.info("Restart pressed, clearing state")
            user_states.pop(message.from_user.id, None)
            await message.answer("Send me a new Telegram chat/group link to analyze:", reply_markup=ReplyKeyboardRemove())

        return

    # If not a button, treat as a link
    if text.startswith("https://t.me/") or text.startswith("@"):
        # Check cache first
        if text in analysis_cache:
            cached = analysis_cache[text]
            logging.info(f"Using cached results for {text}")

            with open(cached['report_path'], "r", encoding="utf-8") as f:
                content = f.read()

            chunks = [content[i:i + 4000] for i in range(0, len(content), 4000)]
            for chunk in chunks:
                await message.answer(chunk)

            user_states[message.from_user.id] = {
                "status": "ready",
                "user_activity_path": cached['user_activity_path'],
                "message_activity_path": cached['message_activity_path']
            }
            await message.answer("Choose an option:", reply_markup=menu_kb)
            return

        await message.answer("⏳ Processing your request... Please wait a moment.")

        try:
            # For real use uncomment below and comment fake function call
            # report_path = await process_chat_analysis(text)
            report_path = await fake_process_chat_analysis(text)  # test with fake

            if report_path and os.path.exists(report_path):
                results_dir = os.path.join(BASE_DIR, "tg_bot", "data", "results")
                cached_paths = {
                    'report_path': report_path,
                    'user_activity_path': os.path.join(results_dir, "user_activity.png"),
                    'message_activity_path': os.path.join(results_dir, "message_activity.png")
                }
                analysis_cache[text] = cached_paths

                with open(report_path, "r", encoding="utf-8") as f:
                    content = f.read()

                formatted_content = format_report_md(content)

                chunks = [formatted_content[i:i + 4000] for i in range(0, len(formatted_content), 4000)]
                for chunk in chunks:
                    await message.answer(chunk, parse_mode=ParseMode.MARKDOWN_V2)

                user_states[message.from_user.id] = {
                    "status": "ready",
                    "user_activity_path": cached_paths['user_activity_path'],
                    "message_activity_path": cached_paths['message_activity_path']
                }

                await message.answer("Choose an option:", reply_markup=menu_kb)
            else:
                await message.answer("⚠️ Failed to generate the report. Please try again later.")
                logging.warning(f"No report found at path: {report_path}")

        except Exception as e:
            logging.exception("❌ An error occurred during analysis:")
            await message.answer("❌ An unexpected error occurred during analysis.")

    else:
        await message.answer("Hello, please send a valid Telegram group link (e.g., https://t.me/yourgroup).")
