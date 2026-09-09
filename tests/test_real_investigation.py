import os

import pytest

from proofcheck.agent.investigator import InvestigationAgent
from proofcheck.agent.tool_executor import ToolExecutor
from proofcheck.llm.client import LLMClient
from proofcheck.retrieval.corpus import index_sample_corpus
from proofcheck.retrieval.embeddings import EmbeddingService
from proofcheck.retrieval.evidence_retriever import EvidenceRetriever
from proofcheck.retrieval.vector_store import InMemoryVectorStore


@pytest.mark.integration
def test_real_sample_corpus_can_be_investigated():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY is not set.")

    project_id = "al-noor-office-building"

    retriever = EvidenceRetriever(
        embedding_service=EmbeddingService(),
        vector_store=InMemoryVectorStore(),
    )

    chunk_count = index_sample_corpus(
        retriever=retriever,
        corpus_dir="data/sample_project",
        project_id=project_id,
    )

    assert chunk_count == 15

    executor = ToolExecutor(
        retriever=retriever,
        project_id=project_id,
    )

    agent = InvestigationAgent(
        client=LLMClient(),
        tool_executor=executor,
    )

    result = agent.investigate(
        claim=(
            "Is the invoiced flooring quantity of 1,500 m2 "
            "sufficiently supported by the project evidence?"
        ),
        project_id=project_id,
    )

    assert result.blocked is False
    assert result.tool_calls >= 1
    assert result.text
