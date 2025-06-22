import pandas as pd
from collections import defaultdict
import os
import logging

BASE_DIR = os.getenv(
    "TGA_OUTPUT_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
)


def summarize_clusters(
        csv_path=os.path.join(BASE_DIR, "results", "hdbscan_clusters.csv"),
        output_path=os.path.join(BASE_DIR, "results", "cluster_summaries.txt"),
        max_messages_per_cluster=5
):
    """
    Reads clustered messages from CSV, groups them by cluster (excluding -1),
    and writes a readable summary per cluster to a .txt file.
    Filters out clusters with only 1 message.
    """
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        logging.warning(f"❌ Cluster file missing: {csv_path}")
        return

    try:
        df = pd.read_csv(csv_path)

        if 'cluster' not in df.columns or 'text' not in df.columns:
            print("⚠️ Required columns 'cluster' or 'text' missing.")
            logging.warning("⚠️ Missing 'cluster' or 'text' columns in CSV.")
            return

        df = df[df['cluster'] != -1]  # exclude noise
        if df.empty:
            print("⚠️ No valid clusters found (excluding noise).")
            logging.info("⚠️ No valid clusters to summarize.")
            return

        grouped = defaultdict(list)
        for _, row in df.iterrows():
            cluster = row['cluster']
            text = str(row['text']).strip().replace("\n", " ")
            if text:
                grouped[cluster].append(text)

        # Remove clusters with only 1 message
        grouped = {k: v for k, v in grouped.items() if len(v) > 1}

        if not grouped:
            print("⚠️ No clusters with more than 1 message.")
            logging.info("⚠️ Skipping cluster summary due to lack of data.")
            return

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for cluster_id, messages in sorted(grouped.items()):
                f.write(f"--- Cluster {cluster_id} ({len(messages)} messages) ---\n")
                for msg in messages[:max_messages_per_cluster]:
                    f.write(f"• {msg}\n")
                f.write("\n")

        print(f"📁 Cluster summaries saved to {output_path}")
        logging.info(f"✅ Cluster summaries saved to {output_path}")

    except Exception as e:
        logging.error(f"❌ Failed to summarize clusters: {e}")
        print(f"❌ Error summarizing clusters: {e}")
