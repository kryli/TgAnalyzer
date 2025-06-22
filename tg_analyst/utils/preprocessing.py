import re

def preprocess_text(text: str) -> str:
    """
    Clean and normalize input text:
    - Convert to lowercase
    - Remove URLs
    - Remove emojis and special characters (leave Cyrillic, Latin, digits)
    - Normalize whitespace

    Args:
        text (str): Raw input string

    Returns:
        str: Cleaned and normalized string
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)

    # Remove emojis and non-text symbols (optionally keep !?., if needed)
    text = re.sub(r"[^\w\sа-яА-Яa-zA-Z0-9]", "", text)

    # Remove excess whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
