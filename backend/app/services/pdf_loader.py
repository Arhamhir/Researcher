from pypdf import PdfReader

def load_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    return "\n".join(pages_text)
