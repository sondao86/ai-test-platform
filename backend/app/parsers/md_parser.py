"""Markdown document parser — reads .md files as-is."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_md(file_path: str | Path) -> str:
    """Read a Markdown file and return its content as raw text.

    AI agents understand markdown natively, so no additional
    parsing or conversion is needed.

    Args:
        file_path: Path to the Markdown file.

    Returns:
        Raw markdown content as a string.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    logger.info("Parsed Markdown %s: %d characters", file_path.name, len(content))
    return content
