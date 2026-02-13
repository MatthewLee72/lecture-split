import fitz
import pytest
from pathlib import Path

from lecture_split.extractor import extract_slide_texts
from lecture_split.models import SlideText


@pytest.fixture
def sample_pdf(tmp_path) -> Path:
    """Create a small PDF with 3 pages of known text."""
    doc = fitz.open()
    for i, text in enumerate(["Intro to ML", "Linear Regression", "Gradient Descent"]):
        page = doc.new_page(width=720, height=540)
        page.insert_text((72, 72), text, fontsize=24)
    pdf_path = tmp_path / "sample.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_extract_returns_list_of_slide_texts(sample_pdf):
    results = extract_slide_texts(sample_pdf)
    assert isinstance(results, list)
    assert all(isinstance(s, SlideText) for s in results)


def test_extract_correct_page_count(sample_pdf):
    results = extract_slide_texts(sample_pdf)
    assert len(results) == 3


def test_extract_page_numbers_are_one_indexed(sample_pdf):
    results = extract_slide_texts(sample_pdf)
    assert [s.page_number for s in results] == [1, 2, 3]


def test_extract_text_content(sample_pdf):
    results = extract_slide_texts(sample_pdf)
    assert "Intro to ML" in results[0].text
    assert "Linear Regression" in results[1].text
    assert "Gradient Descent" in results[2].text


def test_extract_nonexistent_file_raises():
    with pytest.raises(FileNotFoundError):
        extract_slide_texts(Path("/nonexistent/file.pdf"))
