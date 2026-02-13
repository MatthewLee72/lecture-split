from pathlib import Path

import fitz

from lecture_split.models import SlideText


def extract_slide_texts(pdf_path: Path) -> list[SlideText]:
    """Extract text content from each page of a PDF."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(str(pdf_path))
    slides = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        slides.append(SlideText(page_number=i + 1, text=text))
    doc.close()
    return slides
