# Telegram Group Message Analyzer

## Overview  
This project analyzes Telegram group chat messages using advanced NLP and clustering models, generating insightful reports enhanced by GPT. It includes a Telegram bot to interactively analyze chats and display results.

---

## Project Structure

- **model_lab/**  
  Contains Jupyter notebook(s) where different models for message analysis are compared and evaluated. This is the experimental part to select the best models.

- **tg_analyst/**  
  Core analysis logic: message loading, preprocessing, clustering, topic modeling, report generation, and GPT summarization.

- **tg_bot/**  
  Telegram bot implementation that integrates with `tg_analyst` to provide interactive chat analysis through Telegram.

- **bot_main.py**  
  Entry point script to launch the Telegram bot.

- **venv/**  
  Python virtual environment folder (not committed to git).

---

## Selected Models for Message Analysis

1. **Sentence Embeddings + HDBSCAN**  
   - Discover hidden semantic clusters without predefining the number of topics.  
   - Uses `paraphrase-multilingual-MiniLM-L12-v2` for multilingual embeddings.  
   - HDBSCAN is robust to noise and varying cluster densities, ideal for short Telegram messages.

2. **TF-IDF + NMF (Non-negative Matrix Factorization)**  
   - Extracts interpretable keywords per topic, especially for longer or more detailed messages.  
   - TF-IDF highlights term importance within chat context.  
   - NMF allows for understandable topic decomposition.

---

## Requirements

Install all dependencies via:

```bash
pip install -r requirements.txt
```

---

### Key libraries include:
`telethon`, `pandas`, `nltk`, `pymorphy3`, `gensim`, `matplotlib`, `seaborn`, `wordcloud`, `pyLDAvis`,  
`scikit-learn`, `bertopic`, `sentence-transformers`, `hdbscan`, `umap-learn`, `top2vec`,  
`python-dotenv`, `openai`, `aiogram`.

---

### Environment Variables  
Create a `.env` file with the following keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
TOKENIZERS_PARALLELISM=false
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
SESSION_NAME=session_name_for_telethon
TARGET_CHAT=optional_default_chat
BOT_TOKEN=your_telegram_bot_token
```

---


## How to Run

1. Activate your virtual environment.

2. Launch the Telegram bot:

```bash
python bot_main.py
```
In Telegram, start the bot and send a Telegram group link or username  
(e.g., https://t.me/groupname or @groupname).

The bot will process the chat, generate reports, and allow you to view activity graphs or restart the analysis.

---

## Additional Information

- Logs are stored in `tg_analyst/logs` and `tg_bot/logs`.
- Raw chat data and analysis results are stored in `tg_analyst/data` and `tg_bot/data`.
- Testing scripts (if any) are in the `tests/` directory.
- For details on the analysis pipeline, see `tg_analyst/run_analysis.py` and related utilities.

---

## Contact & Support

For issues or contributions, please open an issue on the GitHub repository or contact the maintainer.

---

Project developed by [Krylov Leonid](https://github.com/kryli) and [Kozlovskii Evgeniy](https://github.com/ekozlovskii) and [Boldyrev Ivan](https://github.com/Boldyrevivan1)





