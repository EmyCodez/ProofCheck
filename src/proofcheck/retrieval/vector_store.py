from dataclasses import dataclass

import numpy as np

from proofcheck.models.schemas import DocumentType, RetrievalChunk


@dataclass
class SearchResult:
    """A retrieved chunk and its similarity score."""

    chunk: RetrievalChunk
    score: float


class InMemoryVectorStore:
    """Small in-memory vector index for ProofCheck evidence."""

    def __init__(self) -> None:
        self._chunks: list[RetrievalChunk] = []
        self._embeddings: list[list[float]] = []

    def add(
        self,
        chunks: list[RetrievalChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Add chunks and their embeddings to the index."""
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have the same length.")

        self._chunks.extend(chunks)
        self._embeddings.extend(embeddings)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        project_id: str | None = None,
        document_type: DocumentType | None = None,
    ) -> list[SearchResult]:
        """Return the most semantically similar chunks after metadata filtering."""
        if not self._chunks:
            return []

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        candidate_indices = [
            index
            for index, chunk in enumerate(self._chunks)
            if (project_id is None or chunk.project_id == project_id)
            and (document_type is None or chunk.document_type == document_type)
        ]

        if not candidate_indices:
            return []

        matrix = np.asarray(
            [self._embeddings[index] for index in candidate_indices],
            dtype=np.float32,
        )
        query = np.asarray(query_embedding, dtype=np.float32)

        scores = matrix @ query
        ranked_positions = np.argsort(scores)[::-1][:top_k]

        return [
            SearchResult(
                chunk=self._chunks[candidate_indices[position]],
                score=float(scores[position]),
            )
            for position in ranked_positions
        ]

    @property
    def size(self) -> int:
        """Return the number of indexed chunks."""
        return len(self._chunks)

