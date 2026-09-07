from proofcheck.models.schemas import DocumentType, RetrievalChunk
from proofcheck.retrieval.embeddings import EmbeddingService
from proofcheck.retrieval.vector_store import InMemoryVectorStore, SearchResult


class EvidenceRetriever:
    """High-level retrieval service for ProofCheck evidence."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: InMemoryVectorStore,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index_chunks(self, chunks: list[RetrievalChunk]) -> None:
        """Embed and index evidence chunks."""
        if not chunks:
            return

        embeddings = self.embedding_service.embed_documents(
            [chunk.text for chunk in chunks]
        )
        self.vector_store.add(chunks, embeddings)

    def search(
        self,
        query: str,
        top_k: int = 5,
        project_id: str | None = None,
        document_type: DocumentType | None = None,
    ) -> list[SearchResult]:
        """Search for evidence relevant to a natural-language query."""
        if not query.strip():
            raise ValueError("Query must not be empty.")

        query_embedding = self.embedding_service.embed_query(query)

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            project_id=project_id,
            document_type=document_type,
        )

