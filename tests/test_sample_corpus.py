from pathlib import Path

from proofcheck.ingestion.parser import parse_document


SAMPLE_PROJECT_DIR = Path("data/sample_project")

SAMPLE_DOCUMENTS = [
    ("01_original_contract.pdf", "DOC-CON-001"),
    ("02_boq.pdf", "DOC-BOQ-001"),
    ("03_change_request_001.pdf", "DOC-CR-001"),
    ("04_approved_change_order_001.pdf", "DOC-CO-001"),
    ("05_work_measurement_record.pdf", "DOC-MR-001"),
    ("06_invoice_INV1042.pdf", "DOC-INV-1042"),
    ("07_correspondence.pdf", "DOC-CORR-001"),
]


def test_sample_project_documents_parse_successfully() -> None:
    for filename, document_id in SAMPLE_DOCUMENTS:
        file_path = SAMPLE_PROJECT_DIR / filename

        assert file_path.exists(), f"Missing sample document: {file_path}"

        result = parse_document(file_path, document_id=document_id)

        assert result.document_id == document_id
        assert result.filename == filename
        assert len(result.pages) > 0
        assert any(page.text.strip() for page in result.pages)
