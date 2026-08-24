import re

def clean_text(raw_text: str) -> str:
    text = raw_text

    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s+\n", "\n\n", text)
    text = re.sub(r"\n\d+\n", "\n", text)
    return text.strip()