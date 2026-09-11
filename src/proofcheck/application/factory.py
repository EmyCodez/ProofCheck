from pathlib import Path

from proofcheck.agent.investigator import InvestigationAgent
from proofcheck.agent.tool_executor import ToolExecutor
from proofcheck.application.service import ProofCheckService
from proofcheck.llm.client import LLMClient
from proofcheck.retrieval.corpus import index_sample_corpus
from proofcheck.retrieval.embeddings import EmbeddingService
from proofcheck.retrieval.evidence_retriever import EvidenceRetriever
from proofcheck.retrieval.vector_store import InMemoryVectorStore


DEFAULT_PROJECT_ID = "project-001"
DEFAULT_CORPUS_DIR = Path("data/sample_project")


def create_proofcheck_service(
    *,
    project_id: str = DEFAULT_PROJECT_ID,
    corpus_dir: str | Path = DEFAULT_CORPUS_DIR,
) -> ProofCheckService:
    """Build the real ProofCheck application service and its dependencies."""

    embedding_service = EmbeddingService()
    vector_store = InMemoryVectorStore()
    retriever = EvidenceRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    index_sample_corpus(
        retriever=retriever,
        corpus_dir=corpus_dir,
        project_id=project_id,
    )

    llm_client = LLMClient()
    tool_executor = ToolExecutor(
        retriever=retriever,
        project_id=project_id,
    )
    investigator = InvestigationAgent(
        client=llm_client,
        tool_executor=tool_executor,
    )

    return ProofCheckService(investigator=investigator)
