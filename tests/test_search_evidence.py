from pathlib import Path

import pytest

from proofcheck.models.schemas import DocumentType
from proofcheck.retrieval.corpus import index_sample_corpus
from proofcheck.retrieval.embeddings import EmbeddingService
from proofcheck.retrieval.evidence_retriever import EvidenceRetriever
from proofcheck.retrieval.vector_store import InMemoryVectorStore
from proofcheck.tools.search_evidence import search_evidence


@pytest.fixture
def retriever():
    embedding_service = EmbeddingService()
    vector_store = InMemoryVectorStore()
    evidence_retriever = EvidenceRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    corpus_dir = Path("data/sample_project")

    index_sample_corpus(
        retriever=evidence_retriever,
        corpus_dir=corpus_dir,
        project_id="al-noor-office-building",
    )

    return evidence_retriever


def test_search_returns_relevant_evidence(retriever):
    results = search_evidence(
        retriever=retriever,
        query="What quantity was approved in CO-001?",
        project_id="al-noor-office-building",
    )

    assert results
    assert any(
        result.document_type == DocumentType.APPROVED_CHANGE.value
        for result in results
    )


def test_search_can_filter_by_document_type(retriever):
    results = search_evidence(
        retriever=retriever,
        query="approved additional flooring quantity",
        project_id="al-noor-office-building",
        document_type=DocumentType.APPROVED_CHANGE.value,
    )

    assert results
    assert all(
        result.document_type == DocumentType.APPROVED_CHANGE.value
        for result in results
    )


def test_search_rejects_empty_query(retriever):
    with pytest.raises(ValueError):
        search_evidence(
            retriever=retriever,
            query="   ",
            project_id="al-noor-office-building",
        )


def test_search_rejects_empty_project_id(retriever):
    with pytest.raises(ValueError):
        search_evidence(
            retriever=retriever,
            query="approved quantity",
            project_id="   ",
        )


def test_search_rejects_unknown_document_type(retriever):
    with pytest.raises(ValueError):
        search_evidence(
            retriever=retriever,
            query="approved quantity",
            project_id="al-noor-office-building",
            document_type="NOT_A_REAL_TYPE",
        )
