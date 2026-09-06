from pathlib import Path

from proofcheck.ingestion.parser import parse_document


SAMPLE_PROJECT_DIR = Path("data/sample_project")

DOCUMENTS = [
    ("01_original_contract.pdf", "DOC-CON-001"),
    ("02_boq.pdf", "DOC-BOQ-001"),
    ("03_change_request_001.pdf", "DOC-CR-001"),
    ("04_approved_change_order_001.pdf", "DOC-CO-001"),
    ("05_work_measurement_record.pdf", "DOC-MR-001"),
    ("06_invoice_INV1042.pdf", "DOC-INV-1042"),
    ("07_correspondence.pdf", "DOC-CORR-001"),
]


def main() -> None:
    for filename, document_id in DOCUMENTS:
        file_path = SAMPLE_PROJECT_DIR / filename
        result = parse_document(file_path, document_id=document_id)

        print("\n" + "=" * 80)
        print(f"DOCUMENT: {result.filename}")
        print(f"DOCUMENT ID: {result.document_id}")
        print("=" * 80)

        for page in result.pages:
            print(f"\n--- PAGE {page.page_number} ---")
            print(page.text)


if __name__ == "__main__":
    main()
