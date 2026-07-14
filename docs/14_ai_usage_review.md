# AI Usage Review

## Tools used

| Tool | Used for | Output accepted? | Notes |
|---|---|---|---|
| Claude (Anthropic) | Drafting the documentation set (docs/01–14), scaffolding the Flask/SQLite app, writing the pytest suite, and structuring the traceability matrix from the requirements/tests/data model I defined | Partially | Structure, wording and code were AI-drafted from constraints I gave it (the raw notes, poor requirements, and case constraints); the specific business decisions (90-day threshold, role model, which slice to build, boundary semantics) were mine and were then re-checked and adjusted where the first draft didn't match my intent |

## Prompts used or summarized
- Prompt/example 1: "Build a Flask + SQLite prototype implementing the Evidence entity (source, owner, freshness_date, category, criticality) linked to an Assessment entity, with a pure business-logic module exposing is_stale(), assessment_readiness() and submit_assessment(role, ...), following exactly the schema I already defined in the data architecture doc — do not invent new fields or tables."
- Prompt/example 2: "Review these 10 poorly-written requirements (R1–R10) and the raw interview notes; identify concrete quality problems (ambiguity, missing acceptance criteria, requirements mixed with implementation) and draft elicitation questions grouped by topic."

## Human review
- What was manually reviewed: every generated requirement's acceptance criteria against the raw interview notes and case constraints (to make sure nothing was invented that the stakeholders didn't actually say or imply); the SQLite schema against the data architecture doc; every automated test's assertions against the actual seeded data (re-ran `pytest -v` myself and read the pass/fail output before treating any test as "done").
- What was changed: the initial generated schema stored a boolean `is_stale` column directly on the evidence table — I rejected this and had it reworked as a computed value at read time, because a stored flag would itself require a background job to stay accurate, which is unnecessary complexity for this scope (see Decision Log DEC-005/DEC-007 reasoning).
- What was rejected: an early draft of REQ-005 that suggested "AMS Manager" could also submit assessments — rejected because neither the interview notes nor the case constraints support that; only "approved AMS leads" (Transition Lead) was explicitly stated by the Security Officer.
- One limitation or risk observed: AI-drafted acceptance criteria can look testable on the surface while still hiding an ambiguous boundary condition (this happened with the original REQ-004 draft, which didn't specify what happens at exactly 90 days — caught during the requirements quality review, not during initial drafting). This is a reminder that AI output needs to be actively stress-tested against edge cases, not just read for plausibility.
