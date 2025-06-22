import os
import logging

BASE_DIR = os.environ.get("TGANALYST_BASE_DIR", os.path.abspath(os.path.dirname(__file__)))
os.environ["TGANALYST_BASE_DIR"] = BASE_DIR


def run_analysis_from_group(json_path: str):
    """
    Runs the full Telegram chat analysis pipeline on the given JSON file.

    Args:
        json_path (str): Path to the JSON file containing chat messages.
    """
    from tg_analyst.utils.analyzer import (
        analyze_messages, plot_message_activity,
        plot_user_activity, cluster_with_embeddings,
        topic_modeling_nmf
    )
    from tg_analyst.report_generator import generate_report
    from tg_analyst import gpt_summary
    from tg_analyst.utils.json_loader import load_json
    from tg_analyst.utils import cluster_utils

    try:
        data = load_json(json_path)
        if not data or not isinstance(data, list):
            raise ValueError("❌ Invalid or empty JSON file")

        logging.info(f"📊 Loaded {len(data)} messages for analysis from {json_path}")

        analyze_messages(json_path)
        plot_message_activity(json_path)
        plot_user_activity(json_path)
        topic_modeling_nmf(json_path)
        cluster_with_embeddings(json_path)

        json_dir = os.path.dirname(json_path)
        results_dir = os.path.join(os.path.dirname(json_dir), "results")
        cluster_csv_path = os.path.join(results_dir, "hdbscan_clusters.csv")
        cluster_summaries_path = os.path.join(results_dir, "cluster_summaries.txt")

        cluster_utils.summarize_clusters(csv_path=cluster_csv_path, output_path=cluster_summaries_path)

        generate_report(results_dir)
        gpt_summary.main(results_dir=results_dir)

        logging.info("✅ Analysis pipeline completed successfully.")

    except Exception as e:
        logging.exception(f"❌ Failed to run analysis pipeline for {json_path}:")
