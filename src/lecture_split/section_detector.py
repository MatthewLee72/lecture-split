import json
import re
import subprocess

from lecture_split.models import SlideText, LecturePlan, Section

SYSTEM_PROMPT = """You are an expert at analyzing lecture slides. Given the text content of each slide, identify logical section boundaries and return a structured JSON response.

You must return ONLY valid JSON with this exact schema:
{
  "lecture_title": "string - the overall lecture title/topic",
  "sections": [
    {
      "title": "string - section title",
      "start_page": int,
      "end_page": int,
      "summary": "string - 1-2 sentence summary of what this section covers"
    }
  ]
}

Rules:
- Every slide page must belong to exactly one section (no gaps, no overlaps)
- Sections must be contiguous (start_page of section N+1 = end_page of section N + 1)
- Group slides by conceptual topic, not by individual slide
- Aim for 3-8 sections for a typical lecture
- The first section's start_page must be 1
- The last section's end_page must equal the total number of slides"""


def detect_sections(
    slides: list[SlideText],
    *,
    model: str = "sonnet",
) -> LecturePlan:
    """Use Claude CLI to identify logical section boundaries in lecture slides."""
    if not slides:
        raise ValueError("Cannot detect sections from empty slide list")

    slides_text = "\n\n".join(
        f"--- SLIDE {s.page_number} ---\n{s.text.replace(chr(0), '')}"
        for s in slides
    )

    user_prompt = (
        f"Analyze these {len(slides)} lecture slides and identify logical sections:\n\n"
        f"{slides_text}"
    )

    result = subprocess.run(
        [
            "claude",
            "--print",
            "--model", model,
            "--system-prompt", SYSTEM_PROMPT,
            "--output-format", "text",
        ],
        input=user_prompt,
        capture_output=True,
        text=True,
        check=True,
    )

    raw = result.stdout.strip()
    # Claude may wrap JSON in markdown code fences — extract it
    fence_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", raw, re.DOTALL)
    if fence_match:
        raw = fence_match.group(1).strip()
    data = json.loads(raw)

    sections = [
        Section(
            title=s["title"],
            start_page=s["start_page"],
            end_page=s["end_page"],
            summary=s["summary"],
        )
        for s in data["sections"]
    ]

    return LecturePlan(lecture_title=data["lecture_title"], sections=sections)
