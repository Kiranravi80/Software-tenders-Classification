import fitz
from pathlib import Path


class PDFParser:

    def extract_text(self, pdf_path):

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        document = fitz.open(pdf_path)

        text = []

        for page in document:
            text.append(page.get_text("text"))

        document.close()

        return "\n".join(text)