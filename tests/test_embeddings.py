from proofcheck.retrieval.embeddings import EmbeddingService


def test_embedding_dimension() -> None:
    service = EmbeddingService()

    assert service.dimension == 384


def test_embed_documents_returns_expected_vectors() -> None:
    service = EmbeddingService()

    embeddings = service.embed_documents(
        [
            "Original flooring quantity is 1000 square metres.",
            "Approved change order adds 300 square metres.",
        ]
    )

    assert len(embeddings) == 2
    assert all(len(vector) == 384 for vector in embeddings)


def test_embed_query_returns_expected_vector() -> None:
    service = EmbeddingService()

    embedding = service.embed_query(
        "What additional flooring quantity was approved?"
    )

    assert len(embedding) == 384

