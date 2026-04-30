# Demo Playbook (the meeting itself)

## Pre-meeting (24 hours before)

- Practice the full demo end-to-end three times. Every demo failure in a
  funder meeting kills the deal.
- Have a backup video recorded in case the live demo fails.
- Have the trace JSON file ready to open if they ask "show me what the AI
  actually did."
- Pre-load the test note. Don't type it live.

## The 8-minute demo (do not exceed 10)

Minute 1: One slide. "Hospitals lose 3-7% of revenue to missed codes and
spend $15-25 per chart on coding labor. We cut that in half with an
AI co-pilot that links every code to the exact evidence in the chart."

Minute 2-4: Live demo.
- Paste a real-looking ED note (de-identified, your test note).
- Show PHI scrubbing (redacted output).
- Show codes appearing with evidence highlighting in the chart.
- Click a code -> the source sentence highlights.
- Click "Show audit packet" -> JSON or PDF with everything.

Minute 5-6: Show the validator catching a deliberate error.
- Add "Patient has Type 1 and Type 2 diabetes" to the note.
- Demo rejects one with Excludes1 reason.
- Add "hypertension and heart failure" -> validator suggests I11.0.

Minute 7: The trace.
- Open trace JSON. "Every tool call, every model call, every decision
  is logged. This is the audit packet your compliance team and a CMS
  auditor would see."

Minute 8: Close. "We're at prototype. With pilot funding, in 12 weeks
we add evidence linking, ED specialty pack, and NCCI validation. With
this pilot we'll prove F1 > 0.93 on your charts. Want to do 50 charts?"

## What to NOT do

- Do not promise "fully autonomous" coding. Be honest: human-in-the-loop
  for inpatient. Autonomy only for narrow, repetitive, low-complexity
  specialties (radiology, simple ED).
- Do not over-claim accuracy. "F1 = X on our 50-chart golden set" is
  honest. "98% accurate" without context is a lie they will catch.
- Do not show the substring search. If they ask about retrieval, say
  "our V2 retrieval stack is hybrid BM25 + embeddings, in development."
- Do not promise a date for HITRUST. Say "we begin SOC 2 Type II
  observation at first pilot, HITRUST kickoff at Month 7."
