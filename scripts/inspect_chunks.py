from pathlib import Path

from proofcheck.ingestion.chunker import chunk_document
from proofcheck.ingestion.parser import parse_document
from proofcheck.models.schemas import DocumentType


SAMPLE_PROJECT_DIR = Path("data/sample_project")

DOCUMENTS = [
    ("01_original_contract.pdf", "DOC-CON-001", DocumentType.CONTRACT),
    ("02_boq.pdf", "DOC-BOQ-001", DocumentType.BOQ),
    ("03_change_request_001.pdf", "DOC-CR-001", DocumentType.CHANGE_REQUEST),
    ("04_approved_change_order_001.pdf", "DOC-CO-001", DocumentType.APPROVED_CHANGE),
    ("05_work_measurement_record.pdf", "DOC-MR-001", DocumentType.WORK_RECORD),
    ("06_invoice_INV1042.pdf", "DOC-INV-1042", DocumentType.INVOICE),
    ("07_correspondence.pdf", "DOC-CORR-001", DocumentType.CORRESPONDENCE),
]


def main() -> None:
    for filename, document_id, document_type in DOCUMENTS:
        file_path = SAMPLE_PROJECT_DIR / filename

        document = parse_document(
            file_path,
            document_id=document_id,
        )

        chunks = chunk_document(
            document=document,
            project_id="PROJ-ALNOOR",
            document_type=document_type,
        )

        print("\n" + "=" * 80)
        print(f"DOCUMENT: {filename}")
        print(f"TYPE: {document_type.value}")
        print(f"CHUNKS: {len(chunks)}")
        print("=" * 80)

        for index, chunk in enumerate(chunks, start=1):
            print(f"\n--- CHUNK {index} ---")
            print(f"ID: {chunk.chunk_id}")
            print(f"TYPE: {chunk.chunk_type}")
            print(f"PAGE: {chunk.page}")
            print(f"SECTION: {chunk.section}")
            print(f"TEXT:\n{chunk.text}")


if __name__ == "__main__":
    main()
