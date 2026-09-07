from proofcheck.models.schemas import DocumentType, RetrievalChunk
from proofcheck.retrieval.embeddings import EmbeddingService
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


def test_vector_store_adds_chunks() -> None:
    chunks = [
        make_chunk(
            "chunk-1",
            "doc-1",
            DocumentType.BOQ,
            "F-01 Office floor tiles: 1,000 m² at AED 80 per m².",
        ),
        make_chunk(
            "chunk-2",
            "doc-2",
            DocumentType.INVOICE,
            "Invoice INV-1042 claims 1,500 m² at AED 80 per m².",
        ),
    ]

    service = EmbeddingService()
    embeddings = service.embed_documents([chunk.text for chunk in chunks])

    store = InMemoryVectorStore()
    store.add(chunks, embeddings)

    assert store.size == 2


def test_semantic_search_returns_relevant_chunk_first() -> None:
    chunks = [
        make_chunk(
            "chunk-boq",
            "doc-boq",
            DocumentType.BOQ,
            "F-01 Office floor tiles: original quantity 1,000 m² at AED 80 per m².",
        ),
        make_chunk(
            "chunk-change",
            "doc-change",
            DocumentType.APPROVED_CHANGE,
            "CO-001 approved an additional 300 m² of flooring at AED 80 per m².",
        ),
        make_chunk(
            "chunk-invoice",
            "doc-invoice",
            DocumentType.INVOICE,
            "Invoice INV-1042 claims 1,500 m² of office floor tiles at AED 80 per m².",
        ),
    ]

    service = EmbeddingService()
    embeddings = service.embed_documents([chunk.text for chunk in chunks])

    store = InMemoryVectorStore()
    store.add(chunks, embeddings)

    query = "What additional flooring quantity was approved?"
    query_embedding = service.embed_query(query)

    results = store.search(query_embedding, top_k=3)

    assert results
    assert results[0].chunk.document_type == DocumentType.APPROVED_CHANGE
    assert "300" in results[0].chunk.text


def test_search_returns_highest_scores_first() -> None:
    chunks = [
        make_chunk(
            "chunk-1",
            "doc-1",
            DocumentType.BOQ,
            "Office floor tiles quantity is 1,000 square metres.",
        ),
        make_chunk(
            "chunk-2",
            "doc-2",
            DocumentType.INVOICE,
            "Invoice claims 1,500 square metres of office floor tiles.",
        ),
    ]

    service = EmbeddingService()
    embeddings = service.embed_documents([chunk.text for chunk in chunks])

    store = InMemoryVectorStore()
    store.add(chunks, embeddings)

    query_embedding = service.embed_query(
        "What quantity of office floor tiles was invoiced?"
    )

    results = store.search(query_embedding, top_k=2)

    assert results[0].score >= results[1].score


def test_project_filter_excludes_other_projects() -> None:
    chunks = [
        RetrievalChunk(
            chunk_id="al-noor-change",
            document_id="doc-1",
            project_id="al-noor-flooring",
            document_type=DocumentType.APPROVED_CHANGE,
            chunk_type="LINE_ITEM",
            text="CO-001 approved an additional 300 m² of flooring.",
        ),
        RetrievalChunk(
            chunk_id="other-project-change",
            document_id="doc-2",
            project_id="other-project",
            document_type=DocumentType.APPROVED_CHANGE,
            chunk_type="LINE_ITEM",
            text="CO-009 approved an additional 300 m² of flooring.",
        ),
    ]

    service = EmbeddingService()
    embeddings = service.embed_documents([chunk.text for chunk in chunks])

    store = InMemoryVectorStore()
    store.add(chunks, embeddings)

    query_embedding = service.embed_query(
        "What additional flooring quantity was approved?"
    )

    results = store.search(
        query_embedding,
        top_k=5,
        project_id="al-noor-flooring",
    )

    assert len(results) == 1
    assert results[0].chunk.project_id == "al-noor-flooring"


def test_document_type_filter_limits_results() -> None:
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

    service = EmbeddingService()
    embeddings = service.embed_documents([chunk.text for chunk in chunks])

    store = InMemoryVectorStore()
    store.add(chunks, embeddings)

    query_embedding = service.embed_query(
        "What additional flooring quantity was approved?"
    )

    results = store.search(
        query_embedding,
        top_k=5,
        document_type=DocumentType.APPROVED_CHANGE,
    )

    assert len(results) == 1
    assert results[0].chunk.document_type == DocumentType.APPROVED_CHANGE
