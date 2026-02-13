from lecture_split.models import LecturePlan

TEACHING_PROMPT = """\
You are a tutor helping me work through a lecture, one section at a time. \
I will give you context about where we are in the lecture and attach the \
corresponding slides as a PDF. Your job is to teach me this section.

**Teaching style:**
- Assume high mathematical and technical sophistication. Don't explain basics unless I ask.
- Prioritize conceptual understanding and intuition over restating slide bullet points. I can read the slides myself—your job is to make me *understand* them.
- Use concrete examples or analogies when a concept is abstract or non-obvious.
- Flag common misconceptions or subtle points the slides gloss over.
- If the slides contain errors or imprecise statements, call them out."""


def generate_preamble(plan: LecturePlan, section_index: int) -> str:
    """Generate a markdown context preamble for a given section."""
    current = plan.sections[section_index]
    total = len(plan.sections)

    lines = [
        TEACHING_PROMPT,
        "",
        "---",
        "",
        f"# Lecture: {plan.lecture_title}",
        f"## Section {section_index + 1} of {total}: {current.title}",
        f"### Slides {current.start_page}\u2013{current.end_page}",
        "",
        "### Full Lecture Outline",
    ]

    for i, s in enumerate(plan.sections):
        prefix = f"{i + 1}."
        page_range = f"(slides {s.start_page}\u2013{s.end_page})"
        if i < section_index:
            lines.append(f"{prefix} {s.title} {page_range} \u2713 covered")
        elif i == section_index:
            lines.append(f"{prefix} **{s.title} {page_range} \u2190 YOU ARE HERE**")
        else:
            lines.append(f"{prefix} {s.title} {page_range}")

    lines.append("")

    if section_index > 0:
        lines.append("### Previous sections covered")
        for i in range(section_index):
            s = plan.sections[i]
            lines.append(f"- **{s.title}**: {s.summary}")
        lines.append("")

    if section_index == 0:
        lines.append("This is the first section of the lecture.")
        lines.append("")

    lines.append("### This section covers")
    lines.append(current.summary)
    lines.append("")
    lines.append(f"### Attach the corresponding section-{section_index + 1:02d}.pdf when prompting.")

    return "\n".join(lines)


def generate_all_preambles(plan: LecturePlan) -> list[str]:
    """Generate preambles for all sections in the plan."""
    return [generate_preamble(plan, i) for i in range(len(plan.sections))]
