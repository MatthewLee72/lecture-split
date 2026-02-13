"""End-to-end integration test: full pipeline from PDF to output directory."""
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import fitz
import pytest
from click.testing import CliRunner

from lecture_split.cli import main


@pytest.fixture
def realistic_pdf(tmp_path) -> Path:
    """Create a 12-page PDF simulating a real lecture."""
    doc = fitz.open()
    slide_contents = [
        "CS229: Machine Learning\nLecture 5\nProfessor Andrew Ng",
        "Today's Agenda\n- Review of linear regression\n- Logistic regression\n- Gradient descent variants\n- Regularization",
        "Review: Linear Regression\nh(x) = theta^T x\nMinimize squared error",
        "Normal Equation\ntheta = (X^T X)^-1 X^T y\nClosed form solution",
        "Logistic Regression\nClassification problems\nOutput: probability",
        "Sigmoid Function\ng(z) = 1 / (1 + e^-z)\nMaps to [0,1]",
        "Decision Boundary\nLinear boundary in feature space\nNon-linear with feature mapping",
        "Gradient Descent\ntheta := theta - alpha * gradient\nIterative optimization",
        "Stochastic Gradient Descent\nUpdate per example\nFaster convergence on large datasets",
        "Mini-batch Gradient Descent\nBest of both worlds\nBatch size hyperparameter",
        "Regularization\nOverfitting prevention\nL1 vs L2 penalties",
        "Summary & Next Steps\nLogistic regression = classification\nSGD for scale\nNext: Neural Networks",
    ]
    for text in slide_contents:
        page = doc.new_page(width=720, height=540)
        y = 72
        for line in text.split("\n"):
            page.insert_text((72, y), line, fontsize=18)
            y += 30
    pdf_path = tmp_path / "cs229_lecture5.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


MOCK_RESPONSE = {
    "lecture_title": "CS229: Machine Learning - Lecture 5",
    "sections": [
        {
            "title": "Introduction & Review",
            "start_page": 1,
            "end_page": 4,
            "summary": "Course intro, agenda overview, and review of linear regression including the normal equation.",
        },
        {
            "title": "Logistic Regression",
            "start_page": 5,
            "end_page": 7,
            "summary": "Introduces logistic regression for classification, the sigmoid function, and decision boundaries.",
        },
        {
            "title": "Gradient Descent Variants",
            "start_page": 8,
            "end_page": 10,
            "summary": "Covers batch, stochastic, and mini-batch gradient descent approaches.",
        },
        {
            "title": "Regularization & Summary",
            "start_page": 11,
            "end_page": 12,
            "summary": "Introduces L1/L2 regularization and summarizes key concepts.",
        },
    ],
}


def _mock_subprocess_result():
    return subprocess.CompletedProcess(
        args=["claude"],
        returncode=0,
        stdout=json.dumps(MOCK_RESPONSE),
        stderr="",
    )


class TestFullPipeline:
    def test_exit_code_zero(self, realistic_pdf, tmp_path):
        out = tmp_path / "sections"
        runner = CliRunner()
        with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
            result = runner.invoke(main, [str(realistic_pdf), "-o", str(out)])
        assert result.exit_code == 0, result.output

    def test_correct_file_count(self, realistic_pdf, tmp_path):
        out = tmp_path / "sections"
        runner = CliRunner()
        with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
            runner.invoke(main, [str(realistic_pdf), "-o", str(out)])
        assert len(list(out.glob("section-*.pdf"))) == 4
        assert len(list(out.glob("section-*.md"))) == 4
        assert (out / "manifest.md").exists()

    def test_pdf_page_counts_match_sections(self, realistic_pdf, tmp_path):
        out = tmp_path / "sections"
        runner = CliRunner()
        with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
            runner.invoke(main, [str(realistic_pdf), "-o", str(out)])
        expected_pages = [4, 3, 3, 2]
        for i, expected in enumerate(expected_pages):
            doc = fitz.open(str(out / f"section-{i+1:02d}.pdf"))
            assert len(doc) == expected, f"section-{i+1:02d}.pdf has {len(doc)} pages, expected {expected}"
            doc.close()

    def test_preambles_have_correct_position(self, realistic_pdf, tmp_path):
        out = tmp_path / "sections"
        runner = CliRunner()
        with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
            runner.invoke(main, [str(realistic_pdf), "-o", str(out)])
        md1 = (out / "section-01.md").read_text()
        assert "Section 1 of 4" in md1
        assert "YOU ARE HERE" in md1
        assert "This is the first section" in md1

        md3 = (out / "section-03.md").read_text()
        assert "Section 3 of 4" in md3
        assert "YOU ARE HERE" in md3
        assert "Introduction & Review" in md3
        assert "Logistic Regression" in md3

    def test_manifest_is_complete(self, realistic_pdf, tmp_path):
        out = tmp_path / "sections"
        runner = CliRunner()
        with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
            runner.invoke(main, [str(realistic_pdf), "-o", str(out)])
        manifest = (out / "manifest.md").read_text()
        assert "CS229" in manifest
        for section in MOCK_RESPONSE["sections"]:
            assert section["title"] in manifest

    def test_total_pages_preserved(self, realistic_pdf, tmp_path):
        out = tmp_path / "sections"
        runner = CliRunner()
        with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
            runner.invoke(main, [str(realistic_pdf), "-o", str(out)])
        total = 0
        for pdf in sorted(out.glob("section-*.pdf")):
            doc = fitz.open(str(pdf))
            total += len(doc)
            doc.close()
        assert total == 12
