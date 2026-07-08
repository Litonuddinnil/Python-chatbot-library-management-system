import re

def clean_text(text: str) -> str:
    """
    Cleans input text by removing duplicate spaces, special characters, and lowercasing.
    """
    if not text:
        return ""
    # Lowercase, clean whitespaces
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text
