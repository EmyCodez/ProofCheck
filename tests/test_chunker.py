from pathlib import Path

from proofcheck.ingestion.chunker import chunk_document
from proofcheck.ingestion.parser import parse_document


SAMPLE_PROJECT_DIR = Path("data/sample_project")


def test_boq_item_stays_as_coherent_chunk() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "02_boq.pdf",
        document_id="DOC-BOQ-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type="BOQ",
    )

    f01_chunks = [
        chunk
        for chunk in chunks
        if "F-01" in chunk.text
    ]

    assert f01_chunks

    text = f01_chunks[0].text

    assert "Office floor tiles" in text
    assert "1,000" in text
    assert "m²" in text
    assert "80" in text
    assert "80,000" in text


def test_measurement_record_preserves_change_reference_and_quantity() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "05_work_measurement_record.pdf",
        document_id="DOC-MR-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type="WORK_RECORD",
    )

    co001_chunks = [
        chunk
        for chunk in chunks
        if "CO-001" in chunk.text
    ]

    assert co001_chunks

    text = co001_chunks[0].text

    assert "Additional office floor tiles" in text
    assert "280" in text
    assert "m²" in text

def test_contract_clause_13_remains_intact() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "01_original_contract.pdf",
        document_id="DOC-CON-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type="CONTRACT",
    )

    clause_chunks = [
        chunk
        for chunk in chunks
        if "Clause 13" in chunk.text
    ]

    assert clause_chunks

    text = clause_chunks[0].text

    assert "Clause 13 — Additional Scope:" in text
    assert "approved Change Order" in text
    assert "approved additional scope" in text

def test_chunks_preserve_document_identity() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "06_invoice_INV1042.pdf",
        document_id="DOC-INV-1042",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type="INVOICE",
    )

    assert chunks

    for chunk in chunks:
        assert chunk.document_id == "DOC-INV-1042"
        assert chunk.project_id == "PROJ-ALNOOR"
        assert chunk.document_type.value == "INVOICE"
        assert chunk.text.strip()
