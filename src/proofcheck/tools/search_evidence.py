from dataclasses import dataclass

from proofcheck.models.schemas import DocumentType, RetrievalChunk
from proofcheck.retrieval.evidence_retriever import EvidenceRetriever


@dataclass(frozen=True)
class EvidenceSearchResult:
    """Structured result returned by the search_evidence tool."""
    chunk_id: str
    document_id: str
    document_type: str
    text: str
    page: int | None
    section: str | None
    score: float


def search_evidence(
    retriever: EvidenceRetriever,
    query: str,
    project_id: str,
    document_type: str | None = None,
    top_k: int = 5,
) -> list[EvidenceSearchResult]:
    """
    Search project evidence using the existing retrieval pipeline.

    The agent interacts with this function rather than accessing
    the vector store directly.
    """

    if not query.strip():
        raise ValueError("Search query must not be empty.")

    if not project_id.strip():
        raise ValueError("Project ID must not be empty.")

    parsed_document_type = None

    if document_type is not None:
        try:
            parsed_document_type = DocumentType(document_type)
        except ValueError as exc:
            raise ValueError(
                f"Unknown document type: {document_type}"
            ) from exc

    results = retriever.search(
        query=query,
        top_k=top_k,
        project_id=project_id,
        document_type=parsed_document_type,
    )

    return [
        EvidenceSearchResult(
            chunk_id=result.chunk.chunk_id,
            document_id=result.chunk.document_id,
            document_type=result.chunk.document_type.value,
            text=result.chunk.text,
            page=result.chunk.page,
            section=result.chunk.section,
            score=result.score,
        )
        for result in results
    ]
