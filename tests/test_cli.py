import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import fitz
import pytest
from click.testing import CliRunner

from lecture_split.cli import main


def _make_test_pdf(path: Path, num_pages: int = 6) -> Path:
    doc = fitz.open()
    topics = [
        "Intro to Deep Learning\nCS231n",
        "What are Neural Networks?\nBiological inspiration",
        "Perceptrons\nSingle layer networks",
        "Backpropagation\nChain rule applied",
        "Training Tips\nBatch norm, dropout",
        "Summary\nKey takeaways",
    ]
    for i in range(num_pages):
        page = doc.new_page(width=720, height=540)
        page.insert_text((72, 72), topics[i % len(topics)], fontsize=20)
    doc.save(str(path))
    doc.close()
    return path


MOCK_API_RESPONSE = {
    "lecture_title": "Intro to Deep Learning",
    "sections": [
        {"title": "Introduction", "start_page": 1, "end_page": 2, "summary": "Introduces deep learning and neural networks."},
        {"title": "Core Concepts", "start_page": 3, "end_page": 5, "summary": "Covers perceptrons, backprop, and training."},
        {"title": "Summary", "start_page": 6, "end_page": 6, "summary": "Recap."},
    ],
}


def _mock_subprocess_result():
    return subprocess.CompletedProcess(
        args=["claude"],
        returncode=0,
        stdout=json.dumps(MOCK_API_RESPONSE),
        stderr="",
    )


def test_cli_runs_successfully(tmp_path):
    pdf_path = _make_test_pdf(tmp_path / "lecture.pdf")
    out_dir = tmp_path / "output"
    runner = CliRunner()
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        result = runner.invoke(main, [str(pdf_path), "--output", str(out_dir)])
    assert result.exit_code == 0, result.output


def test_cli_creates_section_pdfs(tmp_path):
    pdf_path = _make_test_pdf(tmp_path / "lecture.pdf")
    out_dir = tmp_path / "output"
    runner = CliRunner()
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        runner.invoke(main, [str(pdf_path), "--output", str(out_dir)])
    pdfs = sorted(out_dir.glob("section-*.pdf"))
    assert len(pdfs) == 3


def test_cli_creates_section_markdowns(tmp_path):
    pdf_path = _make_test_pdf(tmp_path / "lecture.pdf")
    out_dir = tmp_path / "output"
    runner = CliRunner()
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        runner.invoke(main, [str(pdf_path), "--output", str(out_dir)])
    mds = sorted(out_dir.glob("section-*.md"))
    assert len(mds) == 3


def test_cli_creates_manifest(tmp_path):
    pdf_path = _make_test_pdf(tmp_path / "lecture.pdf")
    out_dir = tmp_path / "output"
    runner = CliRunner()
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        runner.invoke(main, [str(pdf_path), "--output", str(out_dir)])
    manifest = out_dir / "manifest.md"
    assert manifest.exists()
    content = manifest.read_text()
    assert "Intro to Deep Learning" in content


def test_cli_missing_pdf():
    runner = CliRunner()
    result = runner.invoke(main, ["/nonexistent.pdf"])
    assert result.exit_code != 0


def test_cli_manifest_contains_all_sections(tmp_path):
    pdf_path = _make_test_pdf(tmp_path / "lecture.pdf")
    out_dir = tmp_path / "output"
    runner = CliRunner()
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        runner.invoke(main, [str(pdf_path), "--output", str(out_dir)])
    content = (out_dir / "manifest.md").read_text()
    assert "Introduction" in content
    assert "Core Concepts" in content
    assert "Summary" in content


def test_cli_manifest_contains_teaching_prompt(tmp_path):
    pdf_path = _make_test_pdf(tmp_path / "lecture.pdf")
    out_dir = tmp_path / "output"
    runner = CliRunner()
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        runner.invoke(main, [str(pdf_path), "--output", str(out_dir)])
    content = (out_dir / "manifest.md").read_text()
    assert "System Prompt" in content
    assert "You are a tutor" in content
    assert "Teaching style:" in content
