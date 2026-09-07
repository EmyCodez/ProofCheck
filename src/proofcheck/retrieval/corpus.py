from pathlib import Path

from proofcheck.ingestion.chunker import chunk_document
from proofcheck.ingestion.parser import parse_document
from proofcheck.models.schemas import DocumentType
from proofcheck.retrieval.evidence_retriever import EvidenceRetriever


DOCUMENT_TYPES = {
    "01_original_contract.pdf": DocumentType.CONTRACT,
    "02_boq.pdf": DocumentType.BOQ,
    "03_change_request_001.pdf": DocumentType.CHANGE_REQUEST,
    "04_approved_change_order_001.pdf": DocumentType.APPROVED_CHANGE,
    "05_work_measurement_record.pdf": DocumentType.WORK_RECORD,
    "06_invoice_INV1042.pdf": DocumentType.INVOICE,
    "07_correspondence.pdf": DocumentType.CORRESPONDENCE,
}


def index_sample_corpus(
    retriever: EvidenceRetriever,
    corpus_dir: str | Path,
    project_id: str,
) -> int:
    """Parse, chunk, embed, and index the sample project corpus."""
    corpus_path = Path(corpus_dir)

    all_chunks = []

    for filename, document_type in DOCUMENT_TYPES.items():
        file_path = corpus_path / filename

        document = parse_document(
            file_path=file_path,
            document_id=file_path.stem,
        )

        chunks = chunk_document(
            document=document,
            project_id=project_id,
            document_type=document_type,
        )

        all_chunks.extend(chunks)

    retriever.index_chunks(all_chunks)

    return len(all_chunks)

