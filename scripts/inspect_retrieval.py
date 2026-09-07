from pathlib import Path

from proofcheck.models.schemas import DocumentType
from proofcheck.retrieval.corpus import index_sample_corpus
from proofcheck.retrieval.embeddings import EmbeddingService
from proofcheck.retrieval.evidence_retriever import EvidenceRetriever
from proofcheck.retrieval.vector_store import InMemoryVectorStore


PROJECT_ID = "al-noor-flooring"
CORPUS_DIR = Path("data/sample_project")

QUESTIONS = [
    (
        "What was the original F-01 flooring quantity?",
        None,
    ),
    (
        "What additional quantity was requested in CR-001?",
        DocumentType.CHANGE_REQUEST,
    ),
    (
        "What additional quantity was approved in CO-001?",
        DocumentType.APPROVED_CHANGE,
    ),
    (
        "What quantity was actually measured?",
        DocumentType.WORK_RECORD,
    ),
    (
        "What quantity was invoiced?",
        DocumentType.INVOICE,
    ),
    (
        "Was the change formally approved?",
        None,
    ),
    (
        "What does the contract require for payment claims?",
        DocumentType.CONTRACT,
    ),
    (
        "Does the correspondence constitute formal approval?",
        None,
    ),
]


def main() -> None:
    print("Building ProofCheck retrieval index...")
    print()

    retriever = EvidenceRetriever(
        EmbeddingService(),
        InMemoryVectorStore(),
    )

    chunk_count = index_sample_corpus(
        retriever=retriever,
        corpus_dir=CORPUS_DIR,
        project_id=PROJECT_ID,
    )

    print(f"Indexed chunks: {chunk_count}")
    print()

    for number, (question, document_type) in enumerate(QUESTIONS, start=1):
        print("=" * 80)
        print(f"QUESTION {number}: {question}")
        print("=" * 80)

        results = retriever.search(
            query=question,
            top_k=5,
            project_id=PROJECT_ID,
            document_type=document_type,
        )

        if not results:
            print("NO RESULTS")
            print()
            continue

        for rank, result in enumerate(results, start=1):
            chunk = result.chunk

            print(f"\nRank {rank}")
            print(f"Score:        {result.score:.4f}")
            print(f"Document:     {chunk.document_id}")
            print(f"Type:         {chunk.document_type}")
            print(f"Chunk type:   {chunk.chunk_type}")
            print(f"Page:         {chunk.page}")
            print(f"Section:      {chunk.section}")
            print(f"Text:\n{chunk.text}")


if __name__ == "__main__":
    main()

