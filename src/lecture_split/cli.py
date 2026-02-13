from pathlib import Path

import click

from lecture_split.context_generator import generate_all_preambles
from lecture_split.extractor import extract_slide_texts
from lecture_split.section_detector import detect_sections
from lecture_split.splitter import split_pdf


def _generate_manifest(plan) -> str:
    from lecture_split.context_generator import TEACHING_PROMPT

    lines = [
        f"# {plan.lecture_title}",
        "",
        "## System Prompt",
        "",
        TEACHING_PROMPT,
        "",
        "## Lecture Outline",
        "",
    ]
    for i, s in enumerate(plan.sections):
        lines.append(
            f"{i + 1}. **{s.title}** (slides {s.start_page}\u2013{s.end_page}): {s.summary}"
        )
    lines.append("")
    lines.append("## Files")
    lines.append("")
    for i, s in enumerate(plan.sections):
        num = f"{i + 1:02d}"
        lines.append(f"- `section-{num}.pdf` + `section-{num}.md` \u2014 {s.title}")
    return "\n".join(lines)


@click.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory (default: <pdf_name>_sections/)",
)
@click.option(
    "--model", "-m",
    default="sonnet",
    help="Claude model alias or full name (e.g. 'sonnet', 'opus', 'haiku').",
)
def main(pdf_path: Path, output: Path | None, model: str):
    """Split lecture slide PDFs into semantically grouped sections with AI context."""
    if output is None:
        output = pdf_path.parent / f"{pdf_path.stem}_sections"

    click.echo(f"Extracting text from {pdf_path.name}...")
    slides = extract_slide_texts(pdf_path)
    click.echo(f"  Found {len(slides)} slides.")

    click.echo("Detecting section boundaries with Claude...")
    plan = detect_sections(slides, model=model)
    click.echo(f"  Identified {len(plan.sections)} sections in \"{plan.lecture_title}\"")

    click.echo(f"Splitting PDF into {len(plan.sections)} section files...")
    pdf_paths = split_pdf(pdf_path, plan.sections, output)

    click.echo("Generating context preambles...")
    preambles = generate_all_preambles(plan)
    for i, preamble in enumerate(preambles):
        md_path = output / f"section-{i + 1:02d}.md"
        md_path.write_text(preamble)

    manifest_path = output / "manifest.md"
    manifest_path.write_text(_generate_manifest(plan))

    click.echo(f"\nDone! Output written to {output}/")
    click.echo(f"  {len(pdf_paths)} section PDFs")
    click.echo(f"  {len(preambles)} context preambles")
    click.echo(f"  1 manifest.md")
    click.echo(f"\nUsage: paste section-XX.md into your AI chat, then attach section-XX.pdf")
