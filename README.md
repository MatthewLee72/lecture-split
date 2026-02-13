# lecture-split

Split lecture slide PDFs into semantically grouped sections with AI-generated context preambles.

## Why

Lecture slide decks are big. A single PDF can easily run 80+ slides and eat most of an AI chatbot's context window — leaving little room for the actual conversation. Worse, most of those slides aren't relevant to the question you're asking right now.

`lecture-split` breaks a lecture PDF into topical sections and generates a context preamble for each one. Instead of dumping the entire deck into a chat, you feed in only the section you're studying plus a compact summary of everything that came before it. The AI gets the full picture of where the material fits in the lecture, without wasting context on slides you don't need yet.

The result: longer, more useful conversations per section, and an AI that can actually reference surrounding context instead of drowning in 80 pages of slide text.

## Install

```bash
git clone https://github.com/MatthewLee72/lecture-split.git
cd lecture-split
pip install .
```

This installs `lecture-split` as a CLI command available wherever your Python environment is active.

To install it globally (available in every terminal session without activating a venv), use [pipx](https://pipx.pypa.io/):

```bash
pipx install git+https://github.com/MatthewLee72/lecture-split.git
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
