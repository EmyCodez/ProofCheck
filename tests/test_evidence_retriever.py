from proofcheck.models.schemas import DocumentType, RetrievalChunk
from proofcheck.retrieval.embeddings import EmbeddingService
from proofcheck.retrieval.evidence_retriever import EvidenceRetriever
from proofcheck.retrieval.vector_store import InMemoryVectorStore


PROJECT_ID = "al-noor-flooring"


def make_chunk(
    chunk_id: str,
    document_id: str,
    document_type: DocumentType,
    text: str,
) -> RetrievalChunk:
    return RetrievalChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        project_id=PROJECT_ID,
        document_type=document_type,
        chunk_type="LINE_ITEM",
        text=text,
    )


def test_index_chunks_adds_evidence() -> None:
    chunks = [
        make_chunk(
            "chunk-1",
            "doc-1",
            DocumentType.BOQ,
            "F-01 original flooring quantity is 1,000 m².",
        ),
        make_chunk(
            "chunk-2",
            "doc-2",
            DocumentType.APPROVED_CHANGE,
            "CO-001 approved an additional 300 m² of flooring.",
        ),
    ]

    retriever = EvidenceRetriever(
        EmbeddingService(),
        InMemoryVectorStore(),
    )

    retriever.index_chunks(chunks)

    assert retriever.vector_store.size == 2


def test_search_returns_relevant_evidence() -> None:
    chunks = [
        make_chunk(
            "chunk-boq",
            "doc-boq",
            DocumentType.BOQ,
            "F-01 original flooring quantity is 1,000 m².",
        ),
        make_chunk(
            "chunk-change",
            "doc-change",
            DocumentType.APPROVED_CHANGE,
            "CO-001 approved an additional 300 m² of flooring.",
        ),
    ]

    retriever = EvidenceRetriever(
        EmbeddingService(),
        InMemoryVectorStore(),
    )

    retriever.index_chunks(chunks)

    results = retriever.search(
        "What additional flooring quantity was approved?"
    )

    assert results
    assert results[0].chunk.document_type == DocumentType.APPROVED_CHANGE
    assert "300" in results[0].chunk.text


def test_search_supports_project_filter() -> None:
    chunks = [
        RetrievalChunk(
            chunk_id="al-noor",
            document_id="doc-1",
            project_id="al-noor-flooring",
            document_type=DocumentType.APPROVED_CHANGE,
            chunk_type="LINE_ITEM",
            text="CO-001 approved an additional 300 m² of flooring.",
        ),
        RetrievalChunk(
            chunk_id="other-project",
            document_id="doc-2",
            project_id="other-project",
            document_type=DocumentType.APPROVED_CHANGE,
            chunk_type="LINE_ITEM",
            text="CO-009 approved an additional 500 m² of flooring.",
        ),
    ]

    retriever = EvidenceRetriever(
        EmbeddingService(),
        InMemoryVectorStore(),
    )

    retriever.index_chunks(chunks)

    results = retriever.search(
        "What additional flooring quantity was approved?",
        project_id=PROJECT_ID,
    )

    assert len(results) == 1
    assert results[0].chunk.project_id == PROJECT_ID


def test_empty_query_is_rejected() -> None:
    retriever = EvidenceRetriever(
        EmbeddingService(),
        InMemoryVectorStore(),
    )

    try:
        retriever.search("   ")
    except ValueError as exc:
        assert str(exc) == "Query must not be empty."
    else:
        raise AssertionError("Expected ValueError for empty query.")

