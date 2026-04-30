# Target Architecture (V2)

The current (V1, Phases 1-3) architecture is documented in /README.md.
This document describes the production target.

## Seven layers

```
Layer 7  Compliance & Audit
Layer 6  Workflow Integration (Epic FHIR, HL7, encoder export)
Layer 5  Coder UI (evidence highlight, edit tracking, DRG calc)
Layer 4  Reasoning & Validation (NCCI, LCD, MUE, MEAT, POA, DRG)
Layer 3  Coding Agents (single coder + reviewer + query-writer)
Layer 2  Retrieval (hybrid BM25+dense, UMLS normalization, NER)
Layer 1  Ingestion & PHI (FHIR/HL7/CDA, OCR, scrub with audit log)
```

## Request-time pipeline

```
Chart (FHIR bundle or document)
   |
   v
[1] Ingestion + section parser (H&P, progress, op note, DC summary, MAR)
[2] PHI scrubber with audit log + fail-closed
[3] Clinical NER (scispaCy) + UMLS normalization -> candidate concepts
[4] Hybrid retrieval per concept -> top-10 code candidates per system
[5] CODER AGENT: single LLM, all systems, full chart context
       Tools: get_code_details, get_children, lookup_table
       Forced tool-use: submit_codes(code, evidence_chunk_id, reasoning, confidence)
[6] DETERMINISTIC VALIDATOR (pure code, NOT an LLM):
       leaf-code, Excludes1, PCS grammar, NCCI PTP, MUE, LCD/NCD, HCC MEAT,
       active-in-quarter, POA inference, DRG calculation
[7] LLM REVIEWER: only fires on flagged codes (combination rules, sequencing)
[8] QUERY-WRITER AGENT: drafts AHIMA-compliant physician queries when MEAT or
    specificity gaps are detected
   |
   v
Coder UI (evidence-linked, edit-tracked, DRG-aware)
```

## Offline pipelines (Ralph loops)

- Retrieval recall loop: agent reads recall@10 on golden set, regenerates
  synonyms via UMLS, re-indexes, re-evaluates. Exit when recall@10 >= 0.97.
- Prompt evolution loop: F1 on golden set per prompt version, A/B tests,
  accept on F1 improvement with no regression.
- Rule mining loop: read denial logs, find patterns, propose new edits,
  test against historical claims.

## Hardening (cross-cutting)

- Forced tool-use for all structured outputs (no regex JSON parsing)
- Deterministic post-validation overrides LLM verdicts
- asyncio.gather for independent workers
- Per-request token + wall-clock + tool-call budgets with circuit breaker
- Retries with exponential backoff + jitter
- Token attribution per request and per agent
- Frozen golden set + F1 in CI
- Model + prompt + index version pinned with every prediction
- Append-only signed audit log (10-year retention)
- Zero-data-retention with all LLM providers, BAA in place
