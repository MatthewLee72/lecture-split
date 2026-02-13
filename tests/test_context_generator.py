import pytest

from lecture_split.models import LecturePlan, Section
from lecture_split.context_generator import generate_preamble, generate_all_preambles


@pytest.fixture
def plan():
    return LecturePlan(
        lecture_title="Introduction to Machine Learning",
        sections=[
            Section("ML Overview", 1, 3, "Defines ML and categorizes learning types."),
            Section("Linear Regression", 4, 6, "Introduces linear regression and cost function."),
            Section("Gradient Descent", 7, 9, "Covers gradient descent optimization."),
            Section("Summary", 10, 10, "Recap of key concepts."),
        ],
    )


def test_preamble_contains_lecture_title(plan):
    md = generate_preamble(plan, section_index=0)
    assert "Introduction to Machine Learning" in md


def test_preamble_contains_current_section_title(plan):
    md = generate_preamble(plan, section_index=1)
    assert "Linear Regression" in md


def test_preamble_contains_position_indicator(plan):
    md = generate_preamble(plan, section_index=2)
    assert "Section 3 of 4" in md


def test_preamble_marks_covered_sections(plan):
    md = generate_preamble(plan, section_index=2)
    # Sections before current should be marked as covered
    assert "covered" in md.lower() or "✓" in md


def test_preamble_marks_current_section(plan):
    md = generate_preamble(plan, section_index=1)
    assert "YOU ARE HERE" in md or "←" in md


def test_preamble_contains_full_outline(plan):
    md = generate_preamble(plan, section_index=0)
    for section in plan.sections:
        assert section.title in md


def test_preamble_contains_previous_summaries_when_not_first(plan):
    md = generate_preamble(plan, section_index=2)
    assert "Defines ML" in md
    assert "Introduces linear regression" in md


def test_preamble_no_previous_section_for_first(plan):
    md = generate_preamble(plan, section_index=0)
    assert "previous" not in md.lower() or "N/A" in md or "none" in md.lower() or "This is the first section" in md


def test_preamble_contains_slide_range(plan):
    md = generate_preamble(plan, section_index=1)
    assert "4" in md and "6" in md


def test_generate_all_preambles_count(plan):
    results = generate_all_preambles(plan)
    assert len(results) == 4


def test_generate_all_preambles_are_strings(plan):
    results = generate_all_preambles(plan)
    assert all(isinstance(r, str) for r in results)


def test_preamble_contains_teaching_prompt(plan):
    md = generate_preamble(plan, section_index=0)
    assert "You are a tutor" in md
    assert "Teaching style:" in md
    assert "conceptual understanding" in md


def test_every_preamble_contains_teaching_prompt(plan):
    for i in range(len(plan.sections)):
        md = generate_preamble(plan, i)
        assert "You are a tutor" in md
