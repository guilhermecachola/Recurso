# Automated Tests

## Framework used
- PyTest 8.2.0 (see `app/requirements.txt` / `pytest.ini`).

## Test scope
- validation rules (mandatory evidence fields, category/criticality constraints);
- role rules (only TransitionLead can submit);
- evidence freshness (90-day boundary);
- readiness assessment logic (missing critical categories);
- database-backed test scenarios (all tests read/write a real SQLite file, not mocks);
- selected business rules from the change request (stale = flag only, never block).

## Test database / test data

### Persistence option
- SQLite (`tests/test_readiness.db`), created fresh for every test run.

### Database or test data setup
- How the database/test data is created: the `conn` pytest fixture in `tests/test_readiness_database.py` calls `database.init_db(db_path=TEST_DB_PATH, seed=True)`, which executes `app/schema.sql` then `app/seed_data.sql` against a brand-new SQLite file.
- How test data is inserted: entirely via `app/seed_data.sql` (4 users, 5 readiness categories, 2 assessments, 8 evidence records) — the same seed script used for the manual demo, guaranteeing the app and the tests reason about identical data semantics.
- How the database/test data is reset before tests: the fixture deletes any pre-existing `test_readiness.db` before creating it, and deletes it again after each test — every test therefore starts from an identical, reproducible state (no test pollution between tests).

### Test data summary

| Data item | Purpose | Related scenario |
|---|---|---|
| Assessment #1 (complete: Monitoring, DR, Access, Integrations, SLA all present, all fresh) | Happy path | AT-001 |
| Assessment #2 (missing DR and Integrations evidence) | Negative test | AT-002 |
| Assessment #2 / Monitoring evidence dated 2026-03-01 (>90 days before reference date) | Boundary / validation test | AT-003 |
| `alice.lead` (role TransitionLead) | Role/security test — allowed to submit | AT-004 |
| `bruno.contrib` (role Contributor) | Role/security test — denied submission | AT-004 |
| `carla.manager` (role AMSManager), `diana.security` (role SecurityOfficer) | Additional role coverage / evidence ownership | supports AT-001, AT-002 (as evidence owners); `diana.security` also used as the negative case for AT-008 |
| 5 `readiness_question` rows (Monitoring, DR, Access, Integrations, SLA) | Defines the "critical" category set used by every readiness calculation | AT-001, AT-002, AT-003, AT-004 |
| RFC #1 (open, assigned to `bruno.contrib`) *(CR)* | Happy path raise + answer / role-security negative case | AT-005, AT-008 |
| RFC #2 (already answered, `is_faq_candidate=1`) *(CR)* | Boundary case (cannot re-answer) / FAQ-candidate persistence check | AT-007, AT-008 |
| RFC #3 (open, unassigned) *(CR)* | Confirms `assigned_to` is genuinely optional at the schema level | supports data-architecture validation, referenced in docs/10 |

*(Total: 4 users + 5 readiness questions + 2 assessments + 8 evidence rows + 3 RFC rows = 22 records across 5 tables — exceeds the minimum of 8 records across 2+ entities, and includes both valid and invalid/incomplete cases.)*

## Automated tests implemented

| Test ID | Test name | Type | Linked REQ | Uses DB/test data? | Purpose |
|---|---|---|---|---|---|
| AT-001 | `test_at001_happy_path_complete_assessment_is_ready` | Happy path | REQ-003 | Yes | Confirms a fully-evidenced assessment loaded from SQLite is recognized as ready |
| AT-002 | `test_at002_negative_missing_critical_evidence_detected` | Negative | REQ-003 | Yes | Confirms an assessment missing DR/Integrations evidence is detected as incomplete |
| AT-003 | `test_at003_boundary_evidence_freshness_threshold` (+ `test_at003_boundary_uses_real_seeded_stale_record`) | Boundary / validation | REQ-004 | Yes (second test); first is parametrized pure-logic + one DB cross-check | Confirms the 90-day boundary is exact (90 = not stale, 91 = stale) and cross-checks against a real seeded stale record |
| AT-004 | `test_at004_role_contributor_cannot_submit`, `test_at004_role_transition_lead_can_submit_when_ready`, `test_at004_role_transition_lead_blocked_if_evidence_missing` | Role / security | REQ-005, REQ-009 | Yes | Confirms Contributor is denied, TransitionLead succeeds (and persists status), and even TransitionLead is blocked if evidence is missing |

*(9 automated tests total, exceeding the minimum of 4; at least 2 are directly linked to requirements — in fact all are.)*

### RFC tool tests (added by change request — `tests/test_rfc_database.py`)

| Test ID | Test name | Type | Linked REQ | Uses DB/test data? | Purpose |
|---|---|---|---|---|---|
| AT-005 | `test_at005_happy_path_transition_lead_raises_rfc` | Happy path | REQ-012 | Yes | Confirms a TransitionLead can raise an RFC and it is persisted as `open` |
| AT-006 | `test_at006_negative_contributor_cannot_raise_rfc`, `test_at006_negative_missing_title_or_question_rejected` | Negative | REQ-012 | Yes (role test); pure-logic (field validation) | Confirms Contributor cannot raise an RFC, and title/question are mandatory |
| AT-007 | `test_at007_boundary_empty_answer_rejected`, `test_at007_boundary_already_answered_rfc_cannot_be_answered_again` | Boundary / validation | REQ-013 | Yes | Confirms an RFC cannot be answered with empty text, and cannot be answered twice |
| AT-008 | `test_at008_role_security_officer_cannot_answer_rfc`, `test_at008_role_contributor_can_answer_and_result_is_persisted`, `test_at008_answered_rfc_can_be_flagged_as_faq_candidate` | Role / security | REQ-013 | Yes | Confirms only Contributor/TransitionLead can answer, the answer is actually persisted, and an answered RFC can be flagged as an FAQ candidate |

*(8 additional automated tests added by the change request, bringing the total to 17. This exceeds the CR's requirement to update "at least 1 automated test, if affected" — a whole new affected area (RFC) was covered with the same AT-001-style rigor as the original readiness tests.)*

## How to run tests
```bash
# from repository root
cd app && pip install -r requirements.txt && cd ..
python -m pytest -v
```

## Test result
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: <repo>
configfile: pytest.ini
testpaths: tests
collected 17 items

tests/test_readiness_database.py::test_at001_happy_path_complete_assessment_is_ready PASSED [  5%]
tests/test_readiness_database.py::test_at002_negative_missing_critical_evidence_detected PASSED [ 11%]
tests/test_readiness_database.py::test_at003_boundary_evidence_freshness_threshold[90-False] PASSED [ 17%]
tests/test_readiness_database.py::test_at003_boundary_evidence_freshness_threshold[91-True] PASSED [ 23%]
tests/test_readiness_database.py::test_at003_boundary_evidence_freshness_threshold[30-False] PASSED [ 29%]
tests/test_readiness_database.py::test_at003_boundary_uses_real_seeded_stale_record PASSED [ 35%]
tests/test_readiness_database.py::test_at004_role_contributor_cannot_submit PASSED [ 41%]
tests/test_readiness_database.py::test_at004_role_transition_lead_can_submit_when_ready PASSED [ 47%]
tests/test_readiness_database.py::test_at004_role_transition_lead_blocked_if_evidence_missing PASSED [ 52%]
tests/test_rfc_database.py::test_at005_happy_path_transition_lead_raises_rfc PASSED [ 58%]
tests/test_rfc_database.py::test_at006_negative_contributor_cannot_raise_rfc PASSED [ 64%]
tests/test_rfc_database.py::test_at006_negative_missing_title_or_question_rejected PASSED [ 70%]
tests/test_rfc_database.py::test_at007_boundary_empty_answer_rejected PASSED [ 76%]
tests/test_rfc_database.py::test_at007_boundary_already_answered_rfc_cannot_be_answered_again PASSED [ 82%]
tests/test_rfc_database.py::test_at008_role_security_officer_cannot_answer_rfc PASSED [ 88%]
tests/test_rfc_database.py::test_at008_role_contributor_can_answer_and_result_is_persisted PASSED [ 94%]
tests/test_rfc_database.py::test_at008_answered_rfc_can_be_flagged_as_faq_candidate PASSED [100%]

============================== 17 passed in 1.09s ===============================
```
(Full raw output also stored in `evidence/test_results.md`.)

## Reflection
- What requirement was easiest to test? REQ-003 (missing critical evidence detection) — it is a pure set-difference calculation with no time/role dependency, so the happy-path and negative tests were straightforward to write and reason about.
- What requirement was hardest to test? REQ-004 (staleness) — it required deciding on a fixed `reference_date` for tests instead of `date.today()`, otherwise tests would be flaky/non-reproducible as real time passes; all boundary tests explicitly pass `reference_date=date(2026, 7, 10)` for this reason.
- Did automated tests reveal ambiguity in any requirement? Yes — writing AT-003 exposed that the original REQ-004 wording didn't specify whether the boundary (exactly 90 days) counted as stale or not. This was resolved as "90 days = not yet stale, 91+ = stale" and documented explicitly in REQ-004's acceptance criteria and Decision Log DEC-002.
- How did the database/test data support the scenarios? Using the *same* `seed_data.sql` for both the manual app demo and the automated tests meant the test assertions could reference real, meaningful business scenarios (a genuinely incomplete LATAM transition, a genuinely complete EU transition) instead of synthetic placeholder data, which made the tests easier to explain and defend.
- What changed after the change request? `test_at003_*` and `test_at004_role_transition_lead_can_submit_when_ready` were written/adjusted specifically to prove that staleness never blocks submission (see docs/09_change_request.md) — before the clarification, it would have been equally plausible to write a test asserting the opposite behaviour.
- What would you improve next? Add a dedicated test that submitted assessments become read-only (currently a documented known limitation, see docs/13), and add an automated NFR/performance test (currently REQ-008 is only measured manually per TC-007, not asserted in pytest).
