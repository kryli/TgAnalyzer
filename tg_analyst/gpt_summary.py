import sys
import os

BASE_DIR = os.environ.get("TGANALYST_BASE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from openai import OpenAI
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def prepare_gpt_input(results_dir: str) -> str:
    """
    Collects output files from the given results directory and prepares a formatted prompt
    for GPT-based summarization. Truncates large files to avoid token overflow.
    
    Args:
        results_dir (str): Path to the directory with result files.
        
    Returns:
        str: Formatted text for GPT input.
    """
    nmf_path = os.path.join(results_dir, "nmf_topics.txt")
    clusters_path = os.path.join(results_dir, "hdbscan_clusters.csv")
    cluster_summary_path = os.path.join(results_dir, "cluster_summaries.txt")
    freq_path = os.path.join(results_dir, "word_frequency.csv")
    report_path = os.path.join(results_dir, "report.md")

    nmf_summary = ""
    cluster_summary = ""
    word_freq = ""
    report_text = ""

    if os.path.exists(nmf_path):
        with open(nmf_path, "r", encoding="utf-8") as f:
            nmf_summary = f.read()

    if os.path.exists(cluster_summary_path):
        with open(cluster_summary_path, "r", encoding="utf-8") as f:
            cluster_summary += "\n" + f.read()

    if os.path.exists(freq_path):
        with open(freq_path, "r", encoding="utf-8") as f:
            word_freq = f.read()

    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            report_text = f.read()

    combined = f"""
📊 Final Chat Analysis Summary

--- Topics (NMF) ---
{nmf_summary}

--- Semantic Clusters (HDBSCAN) ---
{cluster_summary}

--- Frequent Words ---
{word_freq}

--- Markdown Report (Optional) ---
{report_text}
"""

    if len(combined) > 12000:
        logging.warning(f"⚠️ GPT input is too long ({len(combined)} chars), truncating.")
        combined = combined[:12000]

    return combined



def ask_gpt(full_text: str) -> str:
    """
    Sends the prepared analysis to GPT and returns the generated summary.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OPENAI_API_KEY not found in .env file.")
        return "API key not found."

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional conversation analyst. Your task is to analyze a Telegram group chat using the outputs of topic modeling (NMF), "
                        "semantic clustering (HDBSCAN), word frequency statistics, and selected message examples from each cluster. "
                        "Your goal is to deeply interpret the group’s behavior and communication patterns, not just summarize raw outputs."
                    )
                },
                {
                    "role": "user",
                    "content": full_text + "\n\n"
                    "Please answer the following questions:\n"
                    "1. What are the main topics discussed in the chat? Group them thematically.\n"
                    "If there any topics or themes that might have been missed by the models but are visible in the sample messages, just add them to point 1\n"
                    "3. How do participants interact with each other? Are there signs of close relationships, informal tone, or leadership?\n"
                    "4. How would you describe the emotional tone and communication style in this group?\n"
                    "5. Based on all the data, write a 5–7 sentence summary of what this Telegram group is mostly about."
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"❌ GPT request failed: {e}")
        return "GPT request failed."


def main(results_dir=None):
    """
    Main entry point: prepares input, gets summary from GPT, and writes it to file.
    """
    if results_dir is None:
        base_dir = os.environ.get("TGANALYST_BASE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        results_dir = os.path.join(base_dir, "data", "results")

    input_text = prepare_gpt_input(results_dir)

    logging.info("🧠 Requesting GPT analysis...")
    result = ask_gpt(input_text)

    output_path = os.path.join(results_dir, "final_analysis_gpt.txt")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not result or result.strip().lower() in {"gpt request failed.", "api key not found."}:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("⚠️ GPT summary could not be generated.\n")
        print("⚠️ GPT summary could not be generated.")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    logging.info(f"✅ Final GPT analysis saved to {output_path}")
    print(f"✅ Final GPT analysis saved to {output_path}")




if __name__ == "__main__":
    main()
