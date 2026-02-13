from pathlib import Path

import fitz

from lecture_split.models import Section


def split_pdf(
    pdf_path: Path, sections: list[Section], output_dir: Path
) -> list[Path]:
    """Split a PDF into separate files based on section boundaries."""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    src = fitz.open(str(pdf_path))
    output_paths = []

    for i, section in enumerate(sections):
        dst = fitz.open()
        # pages are 0-indexed in pymupdf, sections use 1-indexed pages
        dst.insert_pdf(src, from_page=section.start_page - 1, to_page=section.end_page - 1)
        filename = f"section-{i + 1:02d}.pdf"
        out_path = output_dir / filename
        dst.save(str(out_path))
        dst.close()
        output_paths.append(out_path)

    src.close()
    return output_paths
