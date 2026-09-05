from dataclasses import dataclass
from pathlib import Path


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
    Parse a document into page-level text.

    PDF extraction will be implemented separately.
    This function currently defines the ingestion contract.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    return ParsedDocument(
        document_id=document_id,
        filename=path.name,
        pages=[],
    )
