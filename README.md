# ProofCheck — AI Evidence Reconciliation Agent

> Don't just summarize documents. Prove whether they agree.

ProofCheck investigates whether an important business claim is supported by evidence distributed across heterogeneous documents.

## Core Workflow

Evidence → Retrieval → Investigation → Deterministic Validation → Reconciliation → Evidence-backed Result → Human Review

## Possible Outcomes

- `SUPPORTED` — available evidence is sufficiently consistent.
- `REVIEW_REQUIRED` — evidence is incomplete, conflicting, or reveals a material discrepancy.
- `BLOCKED` — a technical dependency such as parsing or retrieval failed, so the system cannot reliably establish the result.

## Engineering Principle

The LLM decides **what to investigate**.

Deterministic systems establish **what the numbers actually say**.

This separation is central to ProofCheck: AI is used for investigation and semantic reasoning, while deterministic logic is used for calculations, consistency checks, and structured validation.

## Safety Boundaries

ProofCheck does not:

- approve or reject payments or business decisions
- determine fraud
- provide legal advice
- modify source documents
- contact external parties
- invent missing evidence
- silently override conflicting evidence

Final decisions remain with a human reviewer.

## Day 1 Foundation

- Canonical data models
- Sample evidence dataset
- 12 golden evaluation scenarios
- Repository structure
- Initial test expectations
- Defined scope and safety boundaries

## Planned Technical Approach

Python, typed tool contracts, structure-aware document parsing and chunking, retrieval/RAG, an LLM investigation agent, deterministic validation, structured review output, and a lightweight UI.

## Development Plan

- **Day 1:** Foundation, data models, sample evidence, evaluation scenarios
- **Day 2:** Document pipeline
- **Day 3:** RAG and retrieval
- **Day 4:** Agent and tools
- **Day 5:** Validation and structured output
- **Day 6:** Safety and failure handling
- **Day 7:** Evaluation
- **Day 8:** UI, deployment, and documentation

## Current Status

🚧 **Day 1 — Foundation complete**

Implementation begins on Day 2.
