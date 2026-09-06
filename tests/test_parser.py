from pathlib import Path

import pymupdf
import pytest

from proofcheck.ingestion.parser import (
    ParsedDocument,
    parse_document,
)


def test_parse_document_requires_existing_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        parse_document(missing_file, document_id="DOC-001")


def test_parse_document_rejects_non_pdf(tmp_path: Path) -> None:
    document = tmp_path / "sample.txt"
    document.write_text("sample content")

    with pytest.raises(ValueError, match="Unsupported document type"):
        parse_document(document, document_id="DOC-001")


def test_parse_document_extracts_pdf_text(tmp_path: Path) -> None:
    document = tmp_path / "sample.pdf"

    pdf = pymupdf.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "ProofCheck test document")
    pdf.save(document)
    pdf.close()

    result = parse_document(document, document_id="DOC-001")

    assert isinstance(result, ParsedDocument)
    assert result.document_id == "DOC-001"
    assert result.filename == "sample.pdf"
    assert len(result.pages) == 1
    assert result.pages[0].page_number == 1
    assert "ProofCheck test document" in result.pages[0].text
