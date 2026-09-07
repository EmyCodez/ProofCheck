from pathlib import Path

import pytest

from proofcheck.models.schemas import DocumentType
from proofcheck.retrieval.corpus import index_sample_corpus
from proofcheck.retrieval.evidence_retriever import EvidenceRetriever
from proofcheck.retrieval.embeddings import EmbeddingService
from proofcheck.retrieval.vector_store import InMemoryVectorStore


CORPUS_DIR = Path("data/sample_project")
PROJECT_ID = "al-noor-office-building"


RETRIEVAL_CASES = [
    (
        "What was the original F-01 flooring quantity?",
        {DocumentType.BOQ, DocumentType.CONTRACT},
    ),
    (
        "What additional quantity was requested in CR-001?",
        {DocumentType.CHANGE_REQUEST},
    ),
    (
        "What additional quantity was approved in CO-001?",
        {DocumentType.APPROVED_CHANGE},
    ),
    (
        "What quantity was actually measured?",
        {DocumentType.WORK_RECORD},
    ),
    (
        "What quantity was invoiced?",
        {DocumentType.INVOICE},
    ),
    (
        "Was the change formally approved?",
        {DocumentType.APPROVED_CHANGE, DocumentType.CONTRACT},
    ),
    (
        "What does the contract require for payment claims?",
        {DocumentType.CONTRACT},
    ),
    (
        "Does the correspondence constitute formal approval?",
        {
            DocumentType.CORRESPONDENCE,
            DocumentType.CONTRACT,
            DocumentType.APPROVED_CHANGE,
        },
    ),
]


@pytest.fixture(scope="module")
def retriever() -> EvidenceRetriever:
    service = EmbeddingService()
    store = InMemoryVectorStore()
    retriever = EvidenceRetriever(service, store)

    index_sample_corpus(
        retriever=retriever,
        corpus_dir=CORPUS_DIR,
        project_id=PROJECT_ID,
    )

    return retriever


@pytest.mark.parametrize(
    ("query", "expected_document_types"),
    RETRIEVAL_CASES,
)
def test_expected_evidence_is_retrieved(
    retriever: EvidenceRetriever,
    query: str,
    expected_document_types: set[DocumentType],
) -> None:
    results = retriever.search(
        query=query,
        top_k=5,
        project_id=PROJECT_ID,
    )

    retrieved_types = {result.chunk.document_type for result in results}

    assert retrieved_types.intersection(expected_document_types), (
        f"No expected evidence found for query: {query!r}. "
        f"Retrieved types: {retrieved_types}"
    )

def test_project_filter_prevents_cross_project_results(
    retriever: EvidenceRetriever,
) -> None:
    results = retriever.search(
        query="What was the original F-01 flooring quantity?",
        top_k=5,
        project_id="nonexistent-project",
    )

    assert results == []


def test_missing_evidence_does_not_create_a_result_from_another_project(
    retriever: EvidenceRetriever,
) -> None:
    results = retriever.search(
        query="What was the approved quantity for the nonexistent electrical package?",
        top_k=5,
        project_id="al-noor-office-building",
    )

    assert all(
        result.chunk.project_id == "al-noor-office-building"
        for result in results
    )


def test_top_k_limits_number_of_results(
    retriever: EvidenceRetriever,
) -> None:
    results = retriever.search(
        query="flooring quantity",
        top_k=1,
        project_id="al-noor-office-building",
    )

    assert len(results) == 1
