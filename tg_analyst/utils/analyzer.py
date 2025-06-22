import os
import re
import json
import logging
from datetime import datetime
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymorphy3
from sentence_transformers import SentenceTransformer

import hdbscan
import umap
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

from tg_analyst.utils.json_loader import load_json
from tg_analyst.utils.preprocessing import preprocess_text

BASE_DIR = os.getenv(
    "TGA_OUTPUT_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
)



# Custom Russian stopwords
stopwords_local = {
    'в', 'на', 'и', 'а', 'но', 'что', 'как', 'уже', 'будет', 'это', 'то',
    'не', 'да', 'с', 'по', 'за', 'от', 'для', 'к', 'о', 'об', 'из', 'при',
    'быть', 'есть', 'его', 'ее', 'их', 'мы', 'вы', 'он', 'она', 'они', 'кто'
}


import logging

def analyze_messages(json_path):
    """
    Analyze Telegram messages and save the top frequent words to a CSV and a plot.

    Parameters:
    - json_path (str): Path to the input JSON file with messages.
    """
    logging.info(f"🔍 Starting word frequency analysis for: {json_path}")

    # Load and validate messages
    data = load_json(json_path)
    messages = [item['text'] for item in data if isinstance(item.get('text'), str) and item['text'].strip()]

    if not messages:
        logging.warning("⚠️ No valid messages with text found for frequency analysis.")
        print("⚠️ No messages with valid text for frequency analysis.")
        return

    # Tokenize and clean
    words = []
    for text in messages:
        tokens = re.findall(r'\b\w+\b', text.lower())
        words.extend([w for w in tokens if w not in stopwords_local])

    if not words:
        logging.warning("⚠️ No valid words found after removing stopwords.")
        print("⚠️ No valid words found after removing stopwords.")
        return

    # Count and filter words
    counter_all = Counter(words)
    word_counts = Counter({word: count for word, count in counter_all.items() if count > 1})

    if not word_counts:
        logging.warning("⚠️ No words with frequency > 1 found.")
        print("⚠️ No words with frequency > 1 found.")
        return

    # Prepare and save top words
    top_words = word_counts.most_common(20)
    os.makedirs(os.path.join(BASE_DIR, 'results'), exist_ok=True)
    df = pd.DataFrame(top_words, columns=['word', 'count'])
    df.to_csv(os.path.join(BASE_DIR, 'results', 'word_frequency.csv'), index=False)

    logging.info("✅ Top frequent words saved to word_frequency.csv")
    print('✅ Word frequency saved to data/results/word_frequency.csv')

    # Plot result
    plot_top_words(word_counts)




import logging

def plot_top_words(word_counts):
    """
    Plot the top 20 most frequent words as a horizontal bar chart
    and save the plot as an image.

    Parameters:
    - word_counts (Counter): A Counter object with word frequencies.
    """
    # Extract the 20 most frequent words
    top_words = word_counts.most_common(20)
    
    if not top_words:
        logging.warning("Not enough data to generate a plot of top words.")
        print("⚠️ Not enough data to plot top words.")
        return

    # Separate words and their counts
    words, counts = zip(*top_words)

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts)
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 20 Frequent Words')
    plt.xlabel('Words')
    plt.ylabel('Count')
    plt.tight_layout()

    # Save plot to file
    output_path = os.path.join(BASE_DIR, 'results', 'top_words.png')
    plt.savefig(output_path)
    plt.close()

    logging.info(f"Word frequency chart saved to {output_path}")
    print(f"📊 Plot saved to {output_path}")



def cluster_with_embeddings(json_path):
    """
    Cluster messages using sentence embeddings + HDBSCAN, save labels and UMAP plot.
    Automatically adjusts clustering sensitivity based on number of messages.
    """
    from sentence_transformers import SentenceTransformer
    import hdbscan
    import umap
    import seaborn as sns

    try:
        data = load_json(json_path)
        texts = [msg['text'].strip() for msg in data if isinstance(msg.get('text'), str) and msg['text'].strip()]

        total_messages = len(texts)
        if total_messages < 10:
            logging.warning(f"⚠️ Not enough messages for clustering (found {total_messages}). Skipping.")
            print(f"⚠️ Not enough messages for clustering (need ≥10, found {total_messages}).")
            return

        # Auto-tune parameters
        if total_messages < 100:
            min_cluster_size = 1
            min_samples = 1
        elif total_messages < 300:
            min_cluster_size = 2
            min_samples = 1
        else:
            min_cluster_size = 3
            min_samples = 2

        logging.info(f"Using HDBSCAN with min_cluster_size={min_cluster_size}, min_samples={min_samples}")
        print(f"🔧 Clustering params: min_cluster_size={min_cluster_size}, min_samples={min_samples}")

        # Embedding
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        embeddings = model.encode(texts, show_progress_bar=True)

        # Clustering
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric='euclidean'
        )
        labels = clusterer.fit_predict(embeddings)

        if len(set(labels)) <= 1:
            logging.warning("⚠️ HDBSCAN found only one cluster or marked all as noise.")
            print("⚠️ Clustering result not meaningful — skipping output.")
            return

        # Save results
        df = pd.DataFrame({'text': texts, 'cluster': labels})
        output_csv = os.path.join(BASE_DIR, 'results', 'hdbscan_clusters.csv')
        df.to_csv(output_csv, index=False)
        logging.info(f"📂 HDBSCAN cluster labels saved to {output_csv}")
        print(f"📂 Clusters saved to {output_csv}")

        # UMAP visualization
        reducer = umap.UMAP(n_components=2, random_state=42)
        embedding_2d = reducer.fit_transform(embeddings)
        df['x'] = embedding_2d[:, 0]
        df['y'] = embedding_2d[:, 1]

        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x='x', y='y', hue='cluster', palette='tab10', legend='full')
        plt.title("HDBSCAN Clusters via UMAP")
        plt.tight_layout()

        output_img = os.path.join(BASE_DIR, 'results', 'hdbscan_umap.png')
        plt.savefig(output_img)
        plt.close()

        logging.info(f"📊 HDBSCAN UMAP plot saved to {output_img}")
        print(f"📊 UMAP plot saved to {output_img}")

    except Exception as e:
        logging.error(f"❌ Error in cluster_with_embeddings: {e}")
        print(f"❌ Error in cluster_with_embeddings: {e}")




def topic_modeling_nmf(json_path, n_topics=10, n_words=10):
    """
    Perform topic modeling using TF-IDF + NMF and save topic summary.
    Skips if too few messages or sparse vocabulary.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import NMF
    from nltk.corpus import stopwords

    try:
        data = load_json(json_path)
        texts = [msg['text'].strip() for msg in data if isinstance(msg.get('text'), str) and msg['text'].strip()]

        if len(texts) < 10:
            logging.warning(f"⚠️ Not enough messages for NMF topic modeling (found {len(texts)}). Skipping.")
            print(f"⚠️ Not enough messages for NMF topic modeling (need ≥10, found {len(texts)}).")
            return

        # Use Russian stopwords from NLTK
        stop_words = stopwords.words("russian")

        logging.info("📐 Vectorizing texts with TF-IDF...")
        tfidf = TfidfVectorizer(max_df=0.95, min_df=2, stop_words=stop_words)
        tfidf_matrix = tfidf.fit_transform(texts)

        if tfidf_matrix.shape[0] == 0 or tfidf_matrix.shape[1] == 0:
            logging.warning("⚠️ TF-IDF matrix is empty after vectorization. Skipping NMF.")
            print("⚠️ TF-IDF matrix is empty — no suitable vocabulary. Skipping NMF.")
            return

        if tfidf_matrix.shape[0] < n_topics:
            n_topics = max(2, tfidf_matrix.shape[0] // 2)
            logging.info(f"ℹ️ Adjusted n_topics to {n_topics} due to small number of documents.")

        logging.info(f"🧠 Fitting NMF with n_topics={n_topics}...")
        nmf = NMF(n_components=n_topics, random_state=42)
        W = nmf.fit_transform(tfidf_matrix)
        H = nmf.components_

        feature_names = tfidf.get_feature_names_out()
        os.makedirs(os.path.join(BASE_DIR, 'results'), exist_ok=True)
        output_path = os.path.join(BASE_DIR, 'results', 'nmf_topics.txt')

        with open(output_path, "w", encoding="utf-8") as f:
            for topic_idx, topic in enumerate(H):
                top = topic.argsort()[:-n_words - 1:-1]
                top_words_str = " ".join([feature_names[i] for i in top])
                f.write(f"Topic {topic_idx + 1}: {top_words_str}\n")

        logging.info(f"✅ NMF topic summary saved to {output_path}")
        print(f"🧠 NMF topics saved to {output_path}")

    except Exception as e:
        logging.error(f"❌ Error in topic_modeling_nmf: {e}")
        print(f"❌ Error in topic_modeling_nmf: {e}")





def plot_message_activity(json_path):
    """
    Plots the number of messages per day using the 'date' field in the dataset.
    Saves the bar chart to a PNG file.
    """
    try:
        data = load_json(json_path)

        # Extract valid dates
        dates = []
        for msg in data:
            date_str = msg.get('date')
            if date_str:
                try:
                    dates.append(datetime.fromisoformat(date_str).date())
                except Exception:
                    continue  # skip invalid dates

        if not dates:
            logging.warning("⚠️ No valid dates found in the dataset.")
            print("⚠️ No valid dates to plot message activity.")
            return

        df = pd.DataFrame({'date': dates})
        df_grouped = df['date'].value_counts().sort_index()

        if df_grouped.empty:
            logging.warning("⚠️ Message count per date is empty after grouping.")
            print("⚠️ No activity to visualize.")
            return

        # Plot
        plt.figure(figsize=(10, 4))
        df_grouped.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title("Message Activity by Date")
        plt.ylabel("Message Count")
        plt.xlabel("Date")
        plt.xticks(rotation=45)
        plt.tight_layout()

        os.makedirs(os.path.join(BASE_DIR, 'results'), exist_ok=True)
        output_path = os.path.join(BASE_DIR, 'results', 'message_activity.png')
        plt.savefig(output_path)
        plt.close()

        logging.info(f"📊 Message activity plot saved to {output_path}")
        print(f"📊 Message activity plot saved to {output_path}")

    except Exception as e:
        logging.error(f"❌ Failed to plot message activity: {e}")
        print(f"❌ Error in plot_message_activity: {e}")

def plot_user_activity(json_path):
    """
    Plots the number of messages per user using 'sender_name' or 'sender_id'.
    Saves the bar chart as a PNG image.
    """
    try:
        data = load_json(json_path)
        df = pd.DataFrame(data)

        if df.empty or 'sender_name' not in df.columns:
            logging.warning("⚠️ No sender_name data available.")
            print("⚠️ Cannot plot user activity — sender_name missing.")
            return

        user_counts = df['sender_name'].fillna("Unknown").value_counts().head(15)

        if user_counts.empty:
            logging.warning("⚠️ No user activity to visualize.")
            print("⚠️ No user activity data to plot.")
            return

        # Plot
        plt.figure(figsize=(10, 6))
        user_counts[::-1].plot(kind='barh', color='orange', edgecolor='black')
        plt.title("Top 15 Most Active Users")
        plt.xlabel("Message Count")
        plt.ylabel("User")
        plt.tight_layout()

        os.makedirs(os.path.join(BASE_DIR, 'results'), exist_ok=True)
        output_path = os.path.join(BASE_DIR, 'results', 'user_activity.png')
        plt.savefig(output_path)
        plt.close()

        logging.info(f"📊 User activity plot saved to {output_path}")
        print(f"📊 User activity plot saved to {output_path}")

    except Exception as e:
        logging.error(f"❌ Failed to plot user activity: {e}")
        print(f"❌ Error in plot_user_activity: {e}")
