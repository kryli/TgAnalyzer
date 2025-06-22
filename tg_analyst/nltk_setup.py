import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
This script downloads necessary NLTK resources for tokenization and stopword processing.
Run it once before the first execution of the analysis pipeline.
"""

import nltk

# Download the Punkt tokenizer for sentence splitting
nltk.download("punkt")

# Download the stopwords list (commonly used in preprocessing)
nltk.download("stopwords")

# Optional: WordNet for lemmatization if needed
nltk.download("wordnet")

# Optional: Additional corpora if you use lemmatizers or taggers
nltk.download("omw-1.4")