import re

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Normalize inputs to lowercase
    text = text.lower()
    # Collapse multiple white spaces into a single space
    text = re.sub(r"\s+", " ", text)
    # Strip unnecessary symbols out leaving alphabetic characters and primary punctuations
    text = re.sub(r"[^a-z0-9.,!? ]", "", text)
    return text.strip()