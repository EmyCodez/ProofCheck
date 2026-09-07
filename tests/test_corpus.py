from pathlib import Path

from proofcheck.models.schemas import DocumentType
from proofcheck.retrieval.corpus import index_sample_corpus
from proofcheck.retrieval.evidence_retriever import EvidenceRetriever
from proofcheck.retrieval.embeddings import EmbeddingService
from proofcheck.retrieval.vector_store import InMemoryVectorStore


PROJECT_ID = "al-noor-flooring"


def test_index_sample_corpus() -> None:
    corpus_dir = Path("data/sample_project")

    retriever = EvidenceRetriever(
        EmbeddingService(),
        InMemoryVectorStore(),
    )

    chunk_count = index_sample_corpus(
        retriever=retriever,
        corpus_dir=corpus_dir,
        project_id=PROJECT_ID,
    )

    assert chunk_count > 0
    assert retriever.vector_store.size == chunk_count


def test_sample_corpus_contains_expected_document_types() -> None:
    corpus_dir = Path("data/sample_project")

    retriever = EvidenceRetriever(
        EmbeddingService(),
        InMemoryVectorStore(),
    )

    index_sample_corpus(
        retriever=retriever,
        corpus_dir=corpus_dir,
        project_id=PROJECT_ID,
    )

    expected_types = {
        DocumentType.CONTRACT,
        DocumentType.BOQ,
        DocumentType.CHANGE_REQUEST,
        DocumentType.APPROVED_CHANGE,
        DocumentType.WORK_RECORD,
        DocumentType.INVOICE,
        DocumentType.CORRESPONDENCE,
    }

    retrieved_types = {
        result.chunk.document_type
        for result in retriever.search(
            "flooring project evidence",
            top_k=20,
            project_id=PROJECT_ID,
        )
    }

    assert expected_types.issubset(retrieved_types)

