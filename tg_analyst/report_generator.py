import os
import logging

def generate_report(results_dir: str):
    """
    Generates a Markdown report summarizing the Telegram chat analysis.
    Includes: word frequency chart, NMF topics, cluster map, message activity chart, and user activity chart.
    Skips sections gracefully if components are missing.

    Args:
        results_dir (str): Path to the results directory where charts and topic files are stored.
    """
    os.makedirs(results_dir, exist_ok=True)
    report_path = os.path.join(results_dir, "report.md")
    topic_path = os.path.join(results_dir, "nmf_topics.txt")

    nmf_topics = ""
    if os.path.exists(topic_path):
        try:
            with open(topic_path, "r", encoding="utf-8") as f:
                nmf_topics = f.read().strip()
        except Exception as e:
            logging.error(f"❌ Failed to read NMF topics from {topic_path}: {e}")

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 🧠 Chat Topic Report\n\n")

            # Word Frequency Chart
            f.write("## 🔹 Word Frequency Analysis\n")
            freq_chart = os.path.join(results_dir, "top_words.png")
            if os.path.exists(freq_chart):
                f.write("![Top Words](top_words.png)\n\n")
            else:
                f.write("_No word frequency chart available._\n\n")

            # NMF Topics
            f.write("## 🔹 Topics by NMF\n")
            if nmf_topics:
                f.write("```\n" + nmf_topics + "\n```\n\n")
            else:
                f.write("_NMF topics not available._\n\n")

            # HDBSCAN Cluster Map
            f.write("## 🔹 Clusters by HDBSCAN\n")
            umap_img = os.path.join(results_dir, "hdbscan_umap.png")
            if os.path.exists(umap_img):
                f.write("![Cluster Map](hdbscan_umap.png)\n\n")
            else:
                f.write("_No cluster visualization available._\n\n")

            # Message Activity Chart
            f.write("## 🔹 Message Activity\n")
            msg_chart = os.path.join(results_dir, "message_activity.png")
            if os.path.exists(msg_chart):
                f.write("![Message Activity](message_activity.png)\n\n")
            else:
                f.write("_Message activity chart not available._\n\n")

            # User Activity Chart
            f.write("## 🔹 User Activity\n")
            user_chart = os.path.join(results_dir, "user_activity.png")
            if os.path.exists(user_chart):
                f.write("![User Activity](user_activity.png)\n\n")
            else:
                f.write("_User activity chart not available._\n\n")

        logging.info(f"✅ Markdown report saved to {report_path}")
        print(f"✅ Markdown report saved to {report_path}")

    except Exception as e:
        logging.error(f"❌ Failed to write report to {report_path}: {e}")
        print(f"❌ Failed to write Markdown report: {e}")
