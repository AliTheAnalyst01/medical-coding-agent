# Vision & Product Thesis

## What we're building

An evidence-linked, audit-defensible AI coding co-pilot for medical coders that
integrates into existing encoder + EHR workflows, drives 2-3x coder
productivity, and reduces denials by surfacing NCCI/LCD/MEAT issues
pre-submission.

We are NOT building "autonomous coding" for inpatient. We are building the
tool the coder uses to get from 2.5 charts/hour to 5+ charts/hour while
producing a defensible audit packet for every code.

## Why now

1. CMS reimbursement is shrinking; coder labor is scarce and expensive.
2. LLMs finally read clinical notes well enough to ground codes in evidence.
3. Hospital coding backlogs are at 3-7 days post-COVID; days-to-bill directly
   affects cash flow.
4. Risk-adjustment audits (RADV) are escalating; payers need MEAT-grade
   chart review at scale.
5. Incumbents (3M/Solventum, Optum) are bolting LLMs onto encoder-era
   architectures. There is a window for an AI-native, evidence-first product.

## Three buyer personas, three products

| Buyer | Pain | Product | Pricing |
|---|---|---|---|
| Hospitals | Coder shortage, days-to-bill, missed CC/MCC | CDI + coding co-pilot integrated to Epic/Cerner | $0.50-$3.00/chart inpatient, $0.10-$0.50/chart outpatient |
| Payers (MA plans) | RADV audits, HCC capture, retrospective review at scale | HCC + MEAT validator with audit packets | $5-$15 per chart reviewed |
| RCM / billing companies | Per-coder margin, denial rate | API-first coding service, white-label UI | per-chart wholesale + revenue share on overturned denials |

## Target wedge for V1: Emergency Department coding

Why ED first:
- High volume (~150M visits/year US), repetitive case mix
- Structured documentation (chief complaint, ROS, exam, MDM)
- Smaller code surface (concentrated in ICD-10-CM J/R/S/T chapters + E/M codes
  99281-99285 + a handful of CPT procedures)
- Existing precedent (Nym Health, CodaMetrix have proven the wedge)
- Faster path to >95% accept rate -> first hospital case study
