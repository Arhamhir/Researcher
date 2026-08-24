import re

def clean_text(raw_text: str) -> str:
    text = raw_text

    # pypdf occasionally emits embedded NUL bytes from certain PDFs.
    # Postgres text/jsonb columns reject the NUL character outright
    # (error 22P05), so strip it here before it reaches anything downstream.
    text = text.replace(chr(0), "")

    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s+\n", "\n\n", text)
    text = re.sub(r"\n\d+\n", "\n", text)
    return text.strip()
