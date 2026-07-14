# Test Results Evidence

## Date/time
2026-07-14 (updated run, after the RFC tool change request) — re-run this and paste your own output/date before final submission.

## Command executed
```
cd app && pip install -r requirements.txt && cd ..
python -m pytest -v
```

## Database/test data used
- Persistence option: SQLite
- Seed file or test data file: `app/schema.sql` + `app/seed_data.sql`, loaded into fresh `tests/test_readiness.db` and `tests/test_rfc.db` files by the `conn` fixtures in `tests/test_readiness_database.py` and `tests/test_rfc_database.py` respectively
- Number of records used: 22 records across 5 tables (4 users, 5 readiness questions, 2 assessments, 8 evidence rows, 3 RFC rows — the last added by the change request)
- Reset strategy before tests: each fixture deletes any pre-existing test database file, recreates it from `schema.sql` + `seed_data.sql` before every test function, and deletes it again afterward

## Result summary
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

## Notes
- Tests passed: 17 / 17
- Tests failed: 0
- Known limitations: REQ-008 (response time NFR) is validated manually per TC-007, not asserted automatically in this pytest suite; submitted assessments are not currently locked against further edits at the database level (documented in docs/13 as a known limitation, not a defect against any stated requirement); RFC answering does not currently support re-opening an answered RFC even if the answer turns out to be wrong (a deliberate simplification, see Decision Log DEC-008 — a real "reopen" flow was judged out of scope for this change request).
