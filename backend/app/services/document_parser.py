"""Unified document parser service."""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.exceptions import DocumentParseError
from app.parsers.docx_parser import parse_docx
from app.parsers.md_parser import parse_md
from app.parsers.pdf_parser import parse_pdf

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md"}


def parse_document(file_path: str | Path) -> str:
    """Parse a document file and return extracted text.

    Supports PDF and DOCX formats.
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise DocumentParseError(
            file_path.name,
            f"Unsupported file type: {extension}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    try:
        if extension == ".pdf":
            return parse_pdf(file_path)
        elif extension == ".docx":
            return parse_docx(file_path)
        elif extension == ".md":
            return parse_md(file_path)
    except FileNotFoundError:
        raise DocumentParseError(file_path.name, "File not found")
    except Exception as e:
        logger.exception("Failed to parse document: %s", file_path.name)
        raise DocumentParseError(file_path.name, str(e))

    raise DocumentParseError(file_path.name, "Unknown error")
