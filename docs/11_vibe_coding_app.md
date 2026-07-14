# Vibe Coding App

## Tool used
- Tool: Claude (Anthropic), used conversationally to scaffold the Flask app, the SQLite schema/seed, and the pytest suite from the requirements and data architecture already defined in `docs/02` and `docs/10`.
- Version / environment: Python 3.12, Flask 3.0.3, pytest 8.2.0 (see `app/requirements.txt`).

## Selected slice
- Option: **A (Evidence validation slice), extended with the REQ-005 role-based submission rule (from Option C)**.
- Why this slice was selected: the interview notes tie evidence traceability and role-restricted submission together directly (Security Officer: "Only approved AMS leads should change readiness assessments. Evidence must be traceable."). Building only Option A would leave REQ-005/REQ-009 (a High-priority requirement) undemonstrated; building the full Option B checklist UI as well was judged out of scope for a one-week timebox. See Decision Log DEC-006 for the full justification and trade-off considered.

## Data architecture used
- Persistence option: SQLite (`app/readiness.db`, created from `app/schema.sql` + `app/seed_data.sql`).
- Main entities/models used: `Assessment`, `Evidence`, `ReadinessQuestion`, `UserRole` — all four entities defined in the data architecture are used by the app.
- Link to `docs/10_data_architecture.md`: the app's `database.py` and `readiness_rules.py` implement exactly the fields, constraints and validation rules documented there; no data model was invented outside that document.

## Requirements implemented

| Requirement | App behaviour |
|---|---|
| REQ-001 | "Add evidence" form on the assessment page requires category, source, owner, freshness_date, criticality |
| REQ-002 | Category dropdown is populated only from `readiness_question`; criticality dropdown is fixed to Critical/Important/Optional |
| REQ-003 | Assessment detail page computes and displays missing critical categories via `readiness_rules.assessment_readiness()` |
| REQ-004 | Each evidence row shows a "STALE" flag when `readiness_rules.is_stale()` returns True (>90 days) |
| REQ-005 | "Submit assessment" form looks up the entered username's role and rejects submission unless role == TransitionLead and no critical category is missing |
| REQ-006 | On successful submission, `assessment.status`, `submitted_by`, `submitted_at` are persisted via `database.mark_submitted()` |
| REQ-007 | Home page (`/`) lists every assessment with its status and computed readiness state |
| REQ-009 | Role check happens in `main.py`'s `submit_assessment` route (server-side), not only via UI disabling |

## App flow
1. Open `/` → see all assessments and their readiness state (ready / missing info).
2. Click an assessment → see its evidence table (with stale flags) and the list of missing critical categories (if any).
3. Fill and submit the "Add evidence" form → new evidence is persisted and the page re-renders with the updated readiness view.
4. Enter a username in "Submit final assessment" → system enforces role + completeness before marking the assessment as submitted.

## Validation / business rules implemented

| Rule | Related REQ | Implemented where |
|---|---|---|
| Evidence must have source, owner, freshness_date | REQ-001 | `main.py::add_evidence` + `schema.sql` NOT NULL |
| Evidence older than 90 days is flagged, never blocks | REQ-004 | `readiness_rules.py::is_stale`, used only for display |
| Assessment ready only if all critical categories have evidence | REQ-003 | `readiness_rules.py::assessment_readiness` |
| Only TransitionLead role can submit | REQ-005, REQ-009 | `readiness_rules.py::can_submit`, enforced in `main.py::submit_assessment` |

## Prompt log

### Prompt 1
"Build a Flask + SQLite prototype implementing the Evidence entity (source, owner, freshness_date, category, criticality) linked to an Assessment entity, with a pure business-logic module (readiness_rules.py) exposing is_stale(), assessment_readiness() and submit_assessment(role, ...), following exactly the schema in docs/10_data_architecture.md — do not invent new fields or tables."

### Result
- What was generated: `schema.sql`, `seed_data.sql`, `database.py`, `readiness_rules.py`, `main.py`, a minimal inline-HTML UI (no separate template engine dependency), and `tests/test_readiness_database.py`.
- What was kept: the full schema, the separation between pure business rules (`readiness_rules.py`) and persistence (`database.py`), and the test structure (fixture-based, fresh SQLite DB per test run).
- What was rejected: an initially generated version stored a boolean `is_stale` column directly on the `evidence` table. This was rejected and reworked as a derived/computed value (see Decision Log DEC-005 rationale) because a stored flag would itself go stale unless recalculated on every read — recomputing at read time from `freshness_date` is simpler and always correct.

## Manual changes

| Change | Reason |
|---|---|
| Removed the stored `is_stale` column, replaced with a runtime calculation in `readiness_rules.is_stale()` | Avoids a second source of truth that could silently become incorrect; keeps the schema aligned with `docs/10_data_architecture.md`'s note on the change request |
| Enforced role check server-side in the Flask route, not only conditionally hiding the submit button in the UI | REQ-009 explicitly requires server-side enforcement, not just UI-level restriction |
| Added parametrized boundary tests for the 90/91-day threshold instead of a single hardcoded example | Directly demonstrates the "flag, not reject" boundary behaviour requested by the change request, rather than just asserting the happy path |
| Split `submit_assessment()` into an explicit two-step check (role first, then completeness) with distinct `reason` values (`unauthorized_role` vs `missing_critical_evidence`) | Makes the negative test cases (TC-008 vs TC-009's failure paths) unambiguous and independently assertable |

## Change request update — RFC tool
The mid-week change request (see `docs/09_change_request.md`) added a new capability: a Transition Lead can raise a structured RFC (title + question, optionally assigned to a Contributor) on any assessment, and a Contributor (or Transition Lead) can answer it. Answered RFCs can be flagged as FAQ candidates for future AMS documentation.

| Requirement | App behaviour |
|---|---|
| REQ-012 | "Raise a new RFC" form on the assessment page; server-side role check restricts creation to `TransitionLead`; title/question are mandatory |
| REQ-013 | "Answer an RFC" form; server-side role check restricts answering to `Contributor`/`TransitionLead`; empty answers and already-answered RFCs are rejected |

This was implemented as a new module (`app/rfc_rules.py`), new database helpers in `app/database.py`, two new Flask routes (`POST /assessment/<id>/rfc`, `POST /rfc/answer`) and a new `rfc` table (see `docs/10_data_architecture.md`) — no existing entity or route was modified, keeping the change additive and low-risk to the already-tested evidence/submission flow.

## How to run the app
```bash
cd app
pip install -r requirements.txt
python database.py     # creates + seeds app/readiness.db from schema.sql + seed_data.sql
python main.py          # starts on http://127.0.0.1:5000
```
Then open http://127.0.0.1:5000 in a browser. Two demo assessments are pre-seeded: assessment #1 is complete/ready, assessment #2 is missing DR and Integrations evidence (to demonstrate the "missing critical information" flow). Demo users: `alice.lead` (TransitionLead, can submit), `bruno.contrib` (Contributor, cannot submit).
