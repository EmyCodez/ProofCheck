from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass
class ParsedPage:
    """Text extracted from one document page."""

    page_number: int
    text: str


@dataclass
class ParsedDocument:
    """Structured result of parsing a document."""

    document_id: str
    filename: str
    pages: list[ParsedPage]


def parse_document(file_path: str | Path, document_id: str) -> ParsedDocument:
    """
    Extract page-level text from a PDF document.

    Raises:
        FileNotFoundError: If the document does not exist.
        ValueError: If the file is not a PDF.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Unsupported document type: {path.suffix}")

    pages: list[ParsedPage] = []

    with pymupdf.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            pages.append(
                ParsedPage(
                    page_number=page_number,
                    text=page.get_text("text").strip(),
                )
            )

    return ParsedDocument(
        document_id=document_id,
        filename=path.name,
        pages=pages,
    )
