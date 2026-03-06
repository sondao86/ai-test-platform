"""PDF document parser using pdfplumber."""

from __future__ import annotations

import logging
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str | Path) -> str:
    """Extract text content from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    pages_text = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages_text.append(f"--- Page {i + 1} ---\n{text}")

    full_text = "\n\n".join(pages_text)
    logger.info("Parsed PDF %s: %d pages, %d characters", file_path.name, len(pages_text), len(full_text))
    return full_text
