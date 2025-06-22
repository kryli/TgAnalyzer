import sys
import os
import json
import logging

# === Base dir setup ===
BASE_DIR = os.environ.get("TGANALYST_BASE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(BASE_DIR)

# === Import modules ===
from tg_analyst.utils.downloader import download_messages
from tg_analyst.utils.analyzer import (
    analyze_messages, plot_message_activity,
    cluster_with_embeddings, topic_modeling_nmf, plot_user_activity
)
from tg_analyst.utils.cluster_utils import summarize_clusters
from tg_analyst.report_generator import generate_report
from tg_analyst.gpt_summary import main as gpt_summary_main

# === Logging setup ===
log_dir = os.path.join(BASE_DIR, 'tg_analyst', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'analysis.log')

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8',
    filemode='w',
)

logging.info("🚀 Starting Telegram Chat Analysis Pipeline...")

# === Config ===
MIN_MESSAGES_FOR_FULL_ANALYSIS = 10
LIMIT_MESSAGES = 500

# === Config flags ===
USE_GPT = False  # True for using GPT
USE_EXISTING_JSON = False  # True — use downloaded file, False — download new
EXISTING_JSON_PATH = os.path.join(BASE_DIR, "model_lab", "messages.json")

# === Step 1: Load or download messages ===
if USE_EXISTING_JSON and os.path.exists(EXISTING_JSON_PATH):
    json_path = EXISTING_JSON_PATH
    print(f"📁 Using existing file: {json_path}")
    logging.info(f"Using existing message file: {json_path}")
else:
    json_path = download_messages(limit=LIMIT_MESSAGES)

if not json_path or not os.path.exists(json_path):
    logging.warning("⚠️ No messages downloaded or file not found. Exiting.")
    print("⚠️ No messages downloaded. Exiting.")
    exit(0)

# === Step 2: Load and validate JSON ===
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data or not isinstance(data, list):
        raise ValueError("Invalid or empty JSON format")

    message_count = len(data)
    print(f"📄 Using data file: {json_path}")
    print(f"💬 Loaded {message_count} messages")
    logging.info(f"✅ Loaded {message_count} messages from {json_path}")

except Exception as e:
    logging.error(f"Failed to load JSON: {e}")
    exit("❌ Error loading JSON.")

# === Step 3: Frequency Analysis ===
try:
    analyze_messages(json_path)
    logging.info("✅ Word frequency analysis completed.")
except Exception as e:
    logging.error(f"analyze_messages() failed: {e}")

# === Step 4: Skip rest if too few messages ===
if message_count < MIN_MESSAGES_FOR_FULL_ANALYSIS:
    print(f"⚠️ Not enough messages for full analysis (min {MIN_MESSAGES_FOR_FULL_ANALYSIS} required). Skipping topic modeling and clustering.")
    logging.warning("Too few messages for NMF and clustering. Pipeline ends here.")
    exit(0)

# === Step 5: Topic Modeling ===
try:
    topic_modeling_nmf(json_path, n_topics=10, n_words=10)
    logging.info("✅ NMF topic modeling completed.")
except Exception as e:
    logging.error(f"topic_modeling_nmf() failed: {e}")

# === Step 6: Plot Message Activity ===
try:
    plot_message_activity(json_path)
    logging.info("✅ Message activity plot generated.")
except Exception as e:
    logging.error(f"plot_message_activity() failed: {e}")

# === Step 7: User Activity Chart ===
try:
    plot_user_activity(json_path)
    logging.info("✅ User activity plot generated.")
except Exception as e:
    logging.error(f"plot_user_activity() failed: {e}")

# === Step 8: Markdown Report ===
try:
    generate_report(os.path.join(BASE_DIR, 'tg_analyst', 'data', 'results'))  # ✅
    logging.info("✅ Markdown report generated.")
except Exception as e:
    logging.error(f"generate_report() failed: {e}")

# === Step 9: Clustering ===
try:
    cluster_with_embeddings(json_path)
    summarize_clusters()
    logging.info("✅ HDBSCAN clustering and summary completed.")
except Exception as e:
    logging.error(f"Clustering or summarizing clusters failed: {e}")

# === Step 10: GPT Summary ===
if USE_GPT:
    try:
        gpt_summary_main()
        logging.info("✅ GPT summary generated.")
    except Exception as e:
        logging.error(f"gpt_summary_main() failed: {e}")
else:
    print("⚠️ GPT summary skipped (USE_GPT=False)")
    logging.info("⚠️ GPT summary skipped by config.")

# === Done ===
logging.info("🏁 Chat analysis pipeline completed successfully.")
print("\n✅ Analysis pipeline completed successfully.")
print(f"📁 Results saved in: {os.path.join(BASE_DIR, 'tg_analyst', 'data', 'results')}")
