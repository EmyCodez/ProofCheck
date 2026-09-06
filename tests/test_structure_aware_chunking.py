from pathlib import Path

from proofcheck.ingestion.chunker import chunk_document
from proofcheck.ingestion.parser import parse_document
from proofcheck.models.schemas import DocumentType


SAMPLE_PROJECT_DIR = Path("data/sample_project")


def test_boq_f01_chunk_preserves_complete_row_context() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "02_boq.pdf",
        document_id="DOC-BOQ-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.BOQ,
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

def test_measurement_co001_chunk_preserves_reference_and_quantity() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "05_work_measurement_record.pdf",
        document_id="DOC-MR-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.WORK_RECORD,
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

def test_approved_change_order_preserves_approval_context() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "04_approved_change_order_001.pdf",
        document_id="DOC-CO-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.APPROVED_CHANGE,
    )

    co001_chunks = [
        chunk
        for chunk in chunks
        if "CO-001" in chunk.text
    ]

    assert co001_chunks

    text = co001_chunks[0].text

    assert "CR-001" in text
    assert "APPROVED" in text
    assert "Additional office floor tiles" in text
    assert "300" in text
    assert "m²" in text
    assert "80" in text
    assert "24,000" in text

def test_invoice_line_item_preserves_claim_context() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "06_invoice_INV1042.pdf",
        document_id="DOC-INV-1042",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.INVOICE,
    )

    invoice_chunks = [
        chunk
        for chunk in chunks
        if "Office floor tiles" in chunk.text
    ]

    assert invoice_chunks

    text = invoice_chunks[0].text

    assert "1,500" in text
    assert "m²" in text
    assert "80" in text
    assert "120,000" in text

def test_correspondence_preserves_logical_message_context() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "07_correspondence.pdf",
        document_id="DOC-CORR-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.CORRESPONDENCE,
    )

    manager_chunks = [
        chunk
        for chunk in chunks
        if "Project Manager" in chunk.text
    ]

    assert manager_chunks

    text = manager_chunks[0].text

    assert "revised layout requires additional flooring" in text
    assert "formal variation documentation" in text

def test_boq_creates_separate_line_item_chunks() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "02_boq.pdf",
        document_id="DOC-BOQ-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.BOQ,
    )

    f01_chunks = [
        chunk
        for chunk in chunks
        if "F-01" in chunk.text
    ]

    f02_chunks = [
        chunk
        for chunk in chunks
        if "F-02" in chunk.text
    ]

    assert len(f01_chunks) == 1
    assert len(f02_chunks) == 1

    assert f01_chunks[0].chunk_type == "LINE_ITEM"
    assert f02_chunks[0].chunk_type == "LINE_ITEM"

    assert "Office floor tiles" in f01_chunks[0].text
    assert "Floor skirting" in f02_chunks[0].text

def test_approved_change_order_preserves_approval_context() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "04_approved_change_order_001.pdf",
        document_id="DOC-CO-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.APPROVED_CHANGE,
    )

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk.document_type == DocumentType.APPROVED_CHANGE
    assert chunk.chunk_type == "LINE_ITEM"

    assert "CO-001" in chunk.text
    assert "CR-001" in chunk.text
    assert "Status: APPROVED" in chunk.text
    assert "300" in chunk.text
    assert "m²" in chunk.text
    assert "80" in chunk.text
    assert "24,000" in chunk.text

def test_work_measurement_preserves_quantity_context() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "05_work_measurement_record.pdf",
        document_id="DOC-MR-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.WORK_RECORD,
    )

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk.document_type == DocumentType.WORK_RECORD
    assert chunk.chunk_type == "LINE_ITEM"

    assert "CO-001" in chunk.text
    assert "Additional office floor tiles" in chunk.text
    assert "280" in chunk.text
    assert "m²" in chunk.text
    assert "Total F-01" in chunk.text
    assert "1,280" in chunk.text

def test_invoice_preserves_claim_line_item_context() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "06_invoice_INV1042.pdf",
        document_id="DOC-INV-1042",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.INVOICE,
    )

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk.document_type == DocumentType.INVOICE
    assert chunk.chunk_type == "LINE_ITEM"

    assert "INV-1042" in chunk.text
    assert "Office floor tiles" in chunk.text
    assert "1,500" in chunk.text
    assert "m²" in chunk.text
    assert "80" in chunk.text
    assert "120,000" in chunk.text

def test_change_request_preserves_requested_quantity_and_status() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "03_change_request_001.pdf",
        document_id="DOC-CR-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.CHANGE_REQUEST,
    )

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk.document_type == DocumentType.CHANGE_REQUEST
    assert chunk.chunk_type == "LINE_ITEM"

    assert "CR-001" in chunk.text
    assert "F-01" in chunk.text
    assert "300" in chunk.text
    assert "m²" in chunk.text
    assert "80" in chunk.text
    assert "24,000" in chunk.text
    assert "SUBMITTED FOR APPROVAL" in chunk.text
    assert "not an approved Change Order" in chunk.text

def test_correspondence_separates_logical_messages() -> None:
    document = parse_document(
        SAMPLE_PROJECT_DIR / "07_correspondence.pdf",
        document_id="DOC-CORR-001",
    )

    chunks = chunk_document(
        document=document,
        project_id="PROJ-ALNOOR",
        document_type=DocumentType.CORRESPONDENCE,
    )

    message_chunks = [
        chunk
        for chunk in chunks
        if chunk.chunk_type == "MESSAGE"
    ]

    assert len(message_chunks) == 2

    assert "Project Manager" in message_chunks[0].text
    assert "Contractor" in message_chunks[0].text
    assert "proceed" in message_chunks[0].text

    assert "Contractor" in message_chunks[1].text
    assert "Project Manager" in message_chunks[1].text
    assert "completed" in message_chunks[1].text
