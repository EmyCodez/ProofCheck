# ProofCheck — AI Evidence Reconciliation Agent

> Don't just summarize documents. Prove whether they agree.

ProofCheck investigates whether an important business claim is supported by evidence distributed across heterogeneous documents.

The system combines **RAG, agentic investigation, deterministic validation, structured reconciliation, safety controls, and human review** to determine whether the available evidence is sufficiently consistent to support a claim.

## Core Problem

Important business claims are often supported by information spread across multiple documents.

A traditional document summarizer can tell you what each document says. ProofCheck goes further:

> **It investigates whether the documents actually support the claim — and surfaces conflicts when they do not.**

### MVP Demonstration

ProofCheck is demonstrated through a construction change-order and invoice reconciliation scenario.

Core claim:

> **“Is this invoiced quantity/cost sufficiently supported by the supplied project evidence?”**

The underlying architecture is intentionally domain-agnostic and can be adapted to other document-heavy workflows.

## Core Workflow

**Evidence → Retrieval → Investigation → Deterministic Validation → Reconciliation → Evidence-backed Result → Human Review**

## Architecture

```text
                    ┌──────────────────────┐
                    │   Business Claim     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Investigation Agent  │
                    │   Gemini + Tools      │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        search_evidence  check_required   compare_evidence
                                        validate_calculation
                │              │              │
                └──────────────┼──────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Deterministic        │
                    │ Reconciliation       │
                    │      Python          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Structured Review    │
                    │ + Findings + Evidence│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Human Review      │
                    └──────────────────────┘
```

### Engineering Principle

> **The LLM decides what to investigate. Deterministic systems establish what the numbers actually say.**

The LLM is responsible for semantic reasoning, evidence selection, and tool use.

Python remains responsible for arithmetic, numeric comparison, consistency checks, structured reconciliation, and final review construction.

This prevents critical numerical conclusions from depending solely on LLM-generated prose.

## Agent Design

ProofCheck uses one bounded investigation agent rather than a multi-agent architecture.

The investigator:

1. Understands the claim.
2. Identifies the evidence required.
3. Searches the supplied evidence when information is unknown.
4. Checks evidence completeness when needed.
5. Compares relevant evidence.
6. Requests deterministic calculations/validation.
7. Follows up when newly discovered evidence creates another investigation question.
8. Stops once sufficient evidence and checks have been obtained.
9. Produces an evidence-backed result.

The investigation is bounded by:

```text
MAX_TOOL_CALLS = 8
```

The LLM-facing investigation surface intentionally exposes only:

* `search_evidence`
* `check_required_evidence`
* `compare_evidence`
* `validate_calculation`

`generate_review_report` remains system-side so that final structured review assembly is not delegated to the LLM.

## Deterministic Validation

Numerical conclusions are handled by deterministic Python functions.

### Numeric comparison

The reconciliation layer can compare expected and observed quantities using an explicit tolerance.

### Calculation validation

The system independently validates:

```text
quantity × unit price = expected total
```

and compares the deterministic result with the observed total.

### Reconciliation

`EvidenceReconciler` converts structured investigation results into:

* evidence IDs
* evidence completeness
* missing evidence
* deterministic findings
* technical failure state

The decision layer then maps the result to one of the supported outcomes.

## Possible Outcomes

* `SUPPORTED` — available evidence is sufficiently consistent.
* `REVIEW_REQUIRED` — evidence is incomplete, conflicting, or reveals a material discrepancy.
* `BLOCKED` — a technical dependency such as parsing, retrieval, or validation failed, so the system cannot reliably establish the result.

A technical failure is **not** treated as missing evidence.

## Safety Boundaries

ProofCheck does not:

* approve or reject payments or business decisions
* approve or reject change orders
* determine fraud
* provide legal advice
* modify source documents
* contact external parties
* invent missing evidence
* silently override conflicting evidence

Supplied document content is treated as **untrusted evidence**, not as instructions to the agent.

Correspondence is not automatically treated as formal approval unless the evidence supports that interpretation.

Final decisions remain with a human reviewer.

## Evidence & Retrieval

The demonstration dataset contains **7 project documents**:

1. Original Contract
2. BOQ
3. Change Request
4. Approved Change Order
5. Work Measurement Record
6. Invoice
7. Correspondence

The document pipeline uses structure-aware chunking so that important relationships are preserved.

Examples include:

* contract clauses
* BOQ table rows with headers
* invoice line items
* change-order approval sections
* measurement records
* complete correspondence messages

Each retrieval chunk preserves metadata such as:

* project ID
* document ID
* document type
* page
* section
* chunk type
* references

### RAG Implementation

* Sentence Transformers
* `all-MiniLM-L6-v2`
* 384-dimensional embeddings
* in-memory vector store
* project/document-type metadata filtering
* semantic retrieval
* evidence reconstruction

The vector store is a **retrieval mechanism, not the source of truth**.

### Retrieval Evaluation

The retrieval layer was evaluated using:

* 8 core retrieval questions
* 3 robustness tests

Latest retrieval evaluation:

**11 passed**

## Evaluation Foundation

ProofCheck includes **12 golden scenarios** covering cases such as:

* perfect match
* invoice exceeding approved quantity
* arithmetic error
* requested but unapproved change
* measurement below approved quantity
* unit mismatch
* latest revision
* ambiguous correspondence
* retrieval failure
* prompt injection in a supplied PDF
* table-context preservation
* requested vs approved quantity

These scenarios are designed to prevent simplistic reconciliation logic.

For example:

> A requested change is not automatically an approved change.

and:

> The BOQ quantity is not automatically treated as the maximum payable quantity.

Verified measurement and approval evidence must retain their semantic roles.

## Sample Reconciliation

The demonstration project is:

**Al Noor Office Building — Flooring Package**

Relevant quantities:

* Original quantity: **1,000 m²**
* Approved additional quantity: **300 m²**
* Approved potential total: **1,300 m²**
* Measured quantity: **1,280 m²**
* Invoiced quantity: **1,500 m²**

The primary discrepancy is:

**1,500 m² invoiced − 1,280 m² measured = 220 m²**

The system returns:

`REVIEW_REQUIRED`

and preserves the supporting evidence for human review.

## Technology

* Python
* Pydantic
* Sentence Transformers
* PyTorch
* Gemini API
* OpenAI-compatible API client
* Gradio
* pytest

## Development Progress

### Day 1 — Foundation ✅

* Canonical data models
* Sample evidence dataset
* 12 golden evaluation scenarios
* Repository structure
* Initial test expectations
* Scope and safety boundaries

### Day 2 — Document Pipeline ✅

* Structure-aware document parsing
* Document-aware chunking
* Metadata preservation
* Seven-document sample evidence pipeline
* Parser/chunker tests

### Day 3 — RAG & Retrieval ✅

* Sentence Transformer embeddings
* In-memory vector store
* Metadata filtering
* Semantic retrieval
* Retrieval evaluation
* 11 retrieval tests passing

### Day 4 — Agent & Reconciliation Foundation ✅

* Gemini LLM integration
* Bounded investigation agent
* Typed tool contracts
* Tool execution
* Deterministic validation
* Structured reconciliation
* Failure handling
* Prompt-injection boundary

### Day 5 — Application & UI ✅

* Gradio application
* Application/service layer
* Real backend connection
* Structured reconciliation state
* Safe operational logging
* Clear/reset interaction
* Visible investigation progress
* Local end-to-end demo

### Day 6 — Reliability & Safety ✅

* Input validation and whitespace sanitization
* Gemini secrets/configuration cleanup
* Investigation tool boundary tightened
* Deterministic EvidenceReconciler integration
* Bounded investigation retained at 8 tool calls
* Prompt guidance strengthened for semantic numeric roles
* Safe operational logging
* Known issue triage
* Successful live Gemini validation

## Verification

Latest full regression suite:

**131 tests passed**

Successful live investigation:

* Model: `gemini-3.5-flash-lite`
* Investigation calls: **7**
* Maximum allowed calls: **8**
* Result: `REVIEW_REQUIRED`
* Deterministic discrepancy: **220 m²**

## Current Known Limitations

The following remain intentionally tracked rather than silently hidden:

* Tool-selection instrumentation can be strengthened to formally verify consistent deterministic comparison invocation.
* An edge case involving incomplete evidence and missing-evidence reporting remains under review.
* The current UI project selection still has a known limitation around mapping the selected project to `project_id`.
* Gemini API availability/rate-limit errors remain an external dependency risk.

These limitations do not change the core safety boundary: the system does not invent evidence or make autonomous business decisions.

## Project Status

🚧 **Day 6 complete — implementation, reliability work, and regression verification complete.**

Next milestone:

**Day 7 — Evaluation**

The focus will be on turning the existing golden evaluation foundation into meaningful end-to-end evaluation evidence covering final outcomes, evidence selection, deterministic validation, safety behavior, and failure recovery.

## Repository

GitHub: `https://github.com/EmyCodez/ProofCheck`
