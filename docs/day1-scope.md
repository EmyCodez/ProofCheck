# Day 1 Scope Lock

## Product
ProofCheck — AI Evidence Reconciliation Agent

## Demonstration domain
Construction change-order and invoice reconciliation.

## Core claim
Is this invoiced quantity/cost sufficiently supported by the supplied project evidence?

## Outcomes
- SUPPORTED
- REVIEW_REQUIRED
- BLOCKED

## Core architecture
Evidence → Retrieval → Investigation → Deterministic Validation → Reconciliation → Evidence-backed Result → Human Review

## Explicit non-goals
- Payment approval/rejection
- Change-order approval
- Fraud determination
- Legal advice
- Automatic external actions
- Source-document modification
- Multi-domain MVP
- Multiple external integrations

## Day 1 engineering deliverables
1. Repository structure
2. Canonical models
3. Sample project evidence
4. 12 golden fixtures
5. Initial tests
6. README and scope lock
