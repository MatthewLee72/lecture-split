import json
import subprocess
from unittest.mock import patch

import pytest

from lecture_split.models import SlideText, LecturePlan
from lecture_split.section_detector import detect_sections


SAMPLE_SLIDES = [
    SlideText(1, "Introduction to Machine Learning\nCS229 - Lecture 1"),
    SlideText(2, "What is Machine Learning?\n- Arthur Samuel (1959)\n- Tom Mitchell (1998)"),
    SlideText(3, "Types of Learning\n- Supervised\n- Unsupervised\n- Reinforcement"),
    SlideText(4, "Linear Regression\nFitting a line to data"),
    SlideText(5, "Cost Function\nJ(theta) = 1/2m sum (h(x) - y)^2"),
    SlideText(6, "Gradient Descent\nIteratively minimize J(theta)"),
    SlideText(7, "Learning Rate\nChoosing alpha"),
    SlideText(8, "Summary\nKey takeaways from today"),
]

MOCK_API_RESPONSE = {
    "lecture_title": "Introduction to Machine Learning",
    "sections": [
        {"title": "Introduction & ML Overview", "start_page": 1, "end_page": 3, "summary": "Defines ML and categorizes learning types."},
        {"title": "Linear Regression", "start_page": 4, "end_page": 5, "summary": "Introduces linear regression and the cost function."},
        {"title": "Gradient Descent", "start_page": 6, "end_page": 7, "summary": "Covers gradient descent optimization and learning rate."},
        {"title": "Summary", "start_page": 8, "end_page": 8, "summary": "Recap of key concepts."},
    ],
}


def _mock_subprocess_result():
    return subprocess.CompletedProcess(
        args=["claude"],
        returncode=0,
        stdout=json.dumps(MOCK_API_RESPONSE),
        stderr="",
    )


def test_detect_sections_returns_lecture_plan():
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        plan = detect_sections(SAMPLE_SLIDES)
    assert isinstance(plan, LecturePlan)


def test_detect_sections_correct_title():
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        plan = detect_sections(SAMPLE_SLIDES)
    assert plan.lecture_title == "Introduction to Machine Learning"


def test_detect_sections_correct_count():
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        plan = detect_sections(SAMPLE_SLIDES)
    assert len(plan.sections) == 4


def test_detect_sections_section_fields():
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        plan = detect_sections(SAMPLE_SLIDES)
    s = plan.sections[0]
    assert s.title == "Introduction & ML Overview"
    assert s.start_page == 1
    assert s.end_page == 3
    assert s.summary == "Defines ML and categorizes learning types."


def test_detect_sections_pages_cover_all_slides():
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()):
        plan = detect_sections(SAMPLE_SLIDES)
    all_pages = set()
    for s in plan.sections:
        all_pages.update(range(s.start_page, s.end_page + 1))
    expected = set(range(1, len(SAMPLE_SLIDES) + 1))
    assert all_pages == expected


def test_detect_sections_calls_claude_cli_with_model():
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()) as mock_run:
        detect_sections(SAMPLE_SLIDES, model="haiku")
    args = mock_run.call_args[0][0]
    assert "claude" in args
    assert "--print" in args
    model_idx = args.index("--model")
    assert args[model_idx + 1] == "haiku"
    # prompt passed via stdin, not as arg
    kwargs = mock_run.call_args[1]
    assert "input" in kwargs
    assert "SLIDE 1" in kwargs["input"]


def test_detect_sections_strips_null_bytes():
    slides_with_nulls = [SlideText(1, "Hello\x00World")]
    with patch("lecture_split.section_detector.subprocess.run", return_value=_mock_subprocess_result()) as mock_run:
        detect_sections(slides_with_nulls)
    prompt = mock_run.call_args[1]["input"]
    assert "\x00" not in prompt
    assert "HelloWorld" in prompt


def test_detect_sections_empty_slides_raises():
    with pytest.raises(ValueError):
        detect_sections([])


def test_detect_sections_handles_json_code_fence():
    fenced = f"```json\n{json.dumps(MOCK_API_RESPONSE)}\n```"
    result = subprocess.CompletedProcess(args=["claude"], returncode=0, stdout=fenced, stderr="")
    with patch("lecture_split.section_detector.subprocess.run", return_value=result):
        plan = detect_sections(SAMPLE_SLIDES)
    assert plan.lecture_title == "Introduction to Machine Learning"
    assert len(plan.sections) == 4


def test_detect_sections_handles_bare_code_fence():
    fenced = f"```\n{json.dumps(MOCK_API_RESPONSE)}\n```"
    result = subprocess.CompletedProcess(args=["claude"], returncode=0, stdout=fenced, stderr="")
    with patch("lecture_split.section_detector.subprocess.run", return_value=result):
        plan = detect_sections(SAMPLE_SLIDES)
    assert plan.lecture_title == "Introduction to Machine Learning"


def test_detect_sections_cli_failure_raises():
    with patch("lecture_split.section_detector.subprocess.run", side_effect=subprocess.CalledProcessError(1, "claude")):
        with pytest.raises(subprocess.CalledProcessError):
            detect_sections(SAMPLE_SLIDES)
