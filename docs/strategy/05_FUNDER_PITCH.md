# Funder Pitch Notes

Three flavors depending on who you're sitting in front of.

## For a HOSPITAL CFO / VP Revenue Cycle

Lead with the metric they own: **cost-to-collect** and **days-in-AR**.

"You spend ~$25 per inpatient chart on coding labor today, and your coders
are 5-7 days behind. Our AI co-pilot pre-codes the chart in 30 seconds with
every code linked to the exact sentence in the documentation. Your coder
reviews and finalizes in 8 minutes instead of 25. That's 3x throughput.

We don't replace your coder. We make her 3x faster, surface CC/MCC she
might miss, and produce the audit packet your compliance team needs.
Pricing is per-chart, so your unit economics improve from day one.

I'd like to run a free 50-chart pilot on a de-identified extract from your
ED to show you the accuracy and speed. No commitment."

Ask: 50-chart pilot + a Letter of Intent if results meet threshold.

## For a HEALTH PLAN (Medicare Advantage)

Lead with: **HCC capture and RADV defensibility**.

"You're getting audited on RADV. CMS is clawing back HCCs that lack MEAT
in the chart. Manual chart review costs you $25-$40 per chart and your
vendors are inconsistent.

We read the chart, identify every HCC-eligible diagnosis, validate MEAT
deterministically (M, E, A, T evidence per CMS criteria), and produce
an audit packet that survives RADV. We can review 10,000 charts in a week
where your vendor takes a quarter.

I'd like to run a 200-chart benchmark against your current vendor. If we
match or beat their HCC capture rate with better evidence, we earn a
production pilot."

Ask: benchmark on 200 charts + paid pilot at $5-8/chart.

## For an RCM / BILLING COMPANY

Lead with: **margin per coder and white-label**.

"Your coders bill out at $X/hr and produce Y charts/hr. Our co-pilot
2-3x's their throughput and reduces denials by surfacing NCCI/LCD pre-
submission. White-label our UI under your brand. Pricing is per-chart
wholesale + revenue share on overturned denials.

You don't change your contracts with hospitals. You just ship more charts
per coder and keep more of the margin."

Ask: 30-day pilot with one specialty queue + revenue-share term sheet.

## What every funder will ask, and how to answer

Q: How accurate is it?
A: "On our 50-chart ED golden set, F1 is X. We measure precision and
recall on every commit. Here's the eval report." [show the CI artifact]

Q: How do you handle hallucination?
A: "Three layers. First, retrieval is grounded against the 73K-code
knowledge base, not free-form generation. Second, every code carries
evidence: the literal sentence in the chart that supports it. Third,
a deterministic validator runs after the LLM and overrides any code
that fails Excludes1, leaf, NCCI, or MEAT checks. The LLM cannot
override the validator."

Q: HIPAA?
A: "Today: in-development, not yet HITRUST/SOC 2. Production roadmap:
SOC 2 Type II observation period starts at first pilot, HITRUST CSF
kickoff at Month 7. We have BAAs and zero-data-retention agreements
with our LLM provider. No PHI is retained by upstream models."

Q: Why not 3M / Optum?
A: "3M and Optum bolt LLMs onto encoder-era architectures. We're AI-native
with evidence linking on every code, deterministic post-validation, and
an active-learning loop on coder edits. We're 1/10 the price for the
specialty wedges we target."

Q: Why you?
A: "I built the prototype solo in [N] weeks. Trace JSON for every request,
F1 measured in CI, full FY2026 guidelines applied by the validator. I'll
hire a CCS-credentialed coder with the seed funding."

Q: What's the moat?
A: "Three things. 1) Evidence-linked audit packets that incumbents can't
retrofit. 2) Specialty-specific golden sets that get better with every
coder edit. 3) Deterministic validation layer over the world's largest
public knowledge base of NCCI/LCD/MEAT rules."
