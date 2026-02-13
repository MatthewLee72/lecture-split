# lecture-split

Split lecture slide PDFs into semantically grouped sections with AI-generated context preambles.

## Install

```bash
cd lecture-split
pip install -e .
```

## Prerequisites

[Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) must be installed and authenticated (e.g. via a Claude (Pro/max subscription):

```bash
npm install -g @anthropic-ai/claude-code
claude setup-token   # if needed
```

## Usage

```bash
# Basic — outputs to <pdf_name>_sections/ in the same directory
lecture-split lecture.pdf

# Custom output directory
lecture-split lecture.pdf -o ./sections/

# Use a different Claude model
lecture-split lecture.pdf -m haiku
```

## Output

```
sections/
├── manifest.md        # Full lecture outline and file index
├── section-01.pdf     # Slides for section 1
├── section-01.md      # Context preamble for section 1
├── section-02.pdf
├── section-02.md
└── ...
```

### manifest.md

A table of contents for the entire lecture with section titles, slide ranges, and summaries.

### section-XX.md

A context preamble that tells the AI chatbot:
- The overall lecture title
- A full outline with a "YOU ARE HERE" marker
- Summaries of all previous sections
- What the current section covers

### section-XX.pdf

The corresponding slide pages extracted from the original PDF.

## Workflow

For each section, paste the `.md` into your AI chat and attach the `.pdf`:

1. Start with `section-01.md` + `section-01.pdf`
2. Have the AI teach you that section
3. Move to `section-02.md` + `section-02.pdf`
4. The preamble carries forward context from previous sections so the AI can make connections

## Running Tests

```bash
pip install pytest
pytest
```
