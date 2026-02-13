import fitz
import pytest
from pathlib import Path

from lecture_split.models import Section
from lecture_split.splitter import split_pdf


@pytest.fixture
def six_page_pdf(tmp_path) -> Path:
    """Create a 6-page PDF with labeled pages."""
    doc = fitz.open()
    for i in range(6):
        page = doc.new_page(width=720, height=540)
        page.insert_text((72, 72), f"Page {i + 1}", fontsize=24)
    pdf_path = tmp_path / "lecture.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def sections():
    return [
        Section("Intro", 1, 2, "Introduction"),
        Section("Middle", 3, 5, "Core content"),
        Section("End", 6, 6, "Conclusion"),
    ]


def test_split_creates_correct_number_of_files(six_page_pdf, sections, tmp_path):
    out = tmp_path / "out"
    results = split_pdf(six_page_pdf, sections, out)
    assert len(results) == 3


def test_split_files_exist(six_page_pdf, sections, tmp_path):
    out = tmp_path / "out"
    results = split_pdf(six_page_pdf, sections, out)
    for path in results:
        assert path.exists()


def test_split_correct_page_counts(six_page_pdf, sections, tmp_path):
    out = tmp_path / "out"
    results = split_pdf(six_page_pdf, sections, out)
    page_counts = []
    for path in results:
        doc = fitz.open(str(path))
        page_counts.append(len(doc))
        doc.close()
    assert page_counts == [2, 3, 1]


def test_split_filenames_are_numbered(six_page_pdf, sections, tmp_path):
    out = tmp_path / "out"
    results = split_pdf(six_page_pdf, sections, out)
    names = [p.name for p in results]
    assert names == ["section-01.pdf", "section-02.pdf", "section-03.pdf"]


def test_split_preserves_content(six_page_pdf, sections, tmp_path):
    out = tmp_path / "out"
    results = split_pdf(six_page_pdf, sections, out)
    doc = fitz.open(str(results[1]))  # "Middle" section: pages 3-5
    text = doc[0].get_text()
    assert "Page 3" in text
    doc.close()


def test_split_creates_output_dir(six_page_pdf, sections, tmp_path):
    out = tmp_path / "nonexistent" / "out"
    split_pdf(six_page_pdf, sections, out)
    assert out.exists()
