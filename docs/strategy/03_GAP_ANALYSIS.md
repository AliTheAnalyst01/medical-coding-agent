# Gap Analysis: V1 (today) vs Production

## Where we are after Phase 3

V1 is a working prototype:
- 5-agent pipeline (coordinator + ICD-CM + ICD-PCS + HCPCS + validator)
- Presidio PHI scrubbing (en_core_web_sm)
- ICD-10-CM graph: Excludes1, etiology pairs, leaf-code set
- FY2026 guidelines loaded into validator (full text, ~6K tokens)
- QUERY_REQUIRED flag for vague documentation
- Streamlit UI with three panels (codes, query-required, trace)
- 48 unit + agent tests passing, 6 integration tests against running server
- JSON trace per request stored in traces/

This proves the agentic pipeline shape. It is NOT a product.

## The 12 gaps to production

| # | Gap | Impact | Solo-feasible in 4-6 weeks? |
|---|---|---|---|
| 1 | Evidence linking (code -> exact sentence in chart) | Buyer dealbreaker | YES |
| 2 | Hybrid retrieval (currently substring search) | Quality dealbreaker | YES, with bge-small + BM25 |
| 3 | CPT / E&M / modifiers | Half the market | NO, needs AMA license |
| 4 | DRG / APC grouper | Productivity dealbreaker for inpatient | PARTIAL (use CMS-published logic for MS-DRG) |
| 5 | NCCI / LCD / MUE edit engine | 60% of denials | YES for NCCI; LCD partial |
| 6 | Query-writer agent (AHIMA-compliant) | CDI productivity | YES |
| 7 | POA inference | HAC penalty risk | YES (rule-based + LLM edge cases) |
| 8 | HCC + MEAT validator | Payer pitch | YES |
| 9 | Active learning from coder edits | Long-term moat | YES (capture, not retrain yet) |
| 10 | HITRUST + SOC 2 + BAA | Buyer dealbreaker | NO at this stage; START process |
| 11 | Audit packet per chart | Legal dealbreaker | YES |
| 12 | Specialty pack (ED first) | Wedge strategy | YES |

Gaps 3 (CPT) and 10 (HITRUST/SOC 2) are the only true blockers requiring
external dependencies. Everything else is solo-engineerable in 4-6 weeks.
