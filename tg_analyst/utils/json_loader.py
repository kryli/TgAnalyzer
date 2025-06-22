import json
import logging
from typing import Any


def save_json(data: Any, path: str) -> None:
    """
    Save Python data as a JSON file.

    Args:
        data (Any): The data to be saved (usually list or dict).
        path (str): The file path where JSON should be saved.
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"✅ JSON saved: {path} ({len(data)} items)" if isinstance(data, list) else f"✅ JSON saved: {path}")
    except Exception as e:
        logging.error(f"❌ Failed to save JSON to {path}: {e}")
        raise


def load_json(path: str) -> Any:
    """
    Load data from a JSON file.

    Args:
        path (str): The file path to load JSON from.

    Returns:
        Any: The loaded data (usually list or dict).
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"📥 JSON loaded: {path} ({len(data)} items)" if isinstance(data, list) else f"📥 JSON loaded: {path}")
        return data
    except Exception as e:
        logging.error(f"❌ Failed to load JSON from {path}: {e}")
        raise
