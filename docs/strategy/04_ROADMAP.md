# 12-Month Roadmap

## Phase 4 (this month, solo): "Demo-ready for funder pitches"

Objective: every funder demo answers "show me one chart, end to end, with
evidence and audit." Six weeks of work.

Week 1: Evidence linking
- Chunk every input note (sentence + section)
- Force coder agent to return (code, chunk_id, reasoning, confidence) via
  forced tool-use schema
- Streamlit UI: click a code, highlight the source sentence

Week 2: Hybrid retrieval V1
- Build embedding index over (code + description + synonyms + Excludes1
  notes) using bge-small or text-embedding-3-small
- BM25 on the same fields
- Reciprocal rank fusion to merge
- Replace substring search in icd_lookup.py

Week 3: ED specialty pack
- 50-chart synthetic ED golden set (use public MIMIC-IV-Note ED subset or
  generate synthetic with GPT-4 + post-validate by hand)
- F1, precision, recall on golden set
- pytest fails CI if F1 drops

Week 4: NCCI + MEAT validator (deterministic)
- Load 05_NCCI_Edits/ data
- Implement check_ncci_ptp(code_a, code_b)
- Implement check_meat(hcc_code, evidence_chunks) using keyword + section
  rules (med change, lab order, exam finding, referral)

Week 5: Query-writer agent + audit packet
- AHIMA-compliant query templates
- Per-chart audit packet (codes, evidence, validations, model versions)
  exported as PDF or signed JSON

Week 6: Polish + pitch deck
- Demo video (3 minutes, real ED chart)
- Architecture diagram
- One-page case study with numbers
- README + strategy docs cleaned up

## Months 4-6: First pilot

- Recruit one CCS-credentialed coder (1099, $80-120/hr) to validate output
  on 200 charts
- Sign first pilot LOI with a community hospital ED department or one
  RCM company (50-bed system or single-specialty group)
- Begin SOC 2 Type II observation period
- Capture coder edit telemetry

## Months 7-9: Compliance + DRG

- HITRUST CSF kickoff
- MS-DRG grouper integration (CMS-published logic)
- Active-learning pipeline over coder edits
- Second pilot

## Months 10-12: Payer play + specialty expansion

- HCC retrospective review module pitched to a regional MA payer
- Radiology specialty pack
- Public benchmark report

## Year 2

- HITRUST certified
- 3-5 specialty packs
- Multi-tenant SaaS + on-prem option
- 1M+ coder edits captured for training
