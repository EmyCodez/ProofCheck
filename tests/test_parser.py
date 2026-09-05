from pathlib import Path

import pytest

from proofcheck.ingestion.parser import (
    ParsedDocument,
    parse_document,
)


def test_parse_document_requires_existing_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        parse_document(missing_file, document_id="DOC-001")


def test_parse_document_returns_structured_result(tmp_path: Path) -> None:
    document = tmp_path / "sample.pdf"
    document.write_text("sample content")

    result = parse_document(document, document_id="DOC-001")

    assert isinstance(result, ParsedDocument)
    assert result.document_id == "DOC-001"
    assert result.filename == "sample.pdf"
    assert result.pages == []
