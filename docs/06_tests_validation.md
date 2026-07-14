# Test Cases and Validation

## TC-001 — Happy path: register valid evidence
- Linked REQ/US: REQ-001 / US-001
- Type: Integration
- Priority: High
- Preconditions: Assessment #1 exists in "draft" status.
- Test data: category=Monitoring, source="Datadog export", owner="carla.manager", freshness_date=2026-06-20, criticality=Critical
- Steps:
  1. Open assessment #1 detail page.
  2. Fill the "Add evidence" form with the test data above.
  3. Submit the form.
- Expected result: A new evidence row is persisted and visible in the assessment's evidence table; no validation error shown.

## TC-002 — Happy path: complete assessment is recognized as ready
- Linked REQ/US: REQ-003 / US-002
- Type: Integration
- Priority: High
- Preconditions: Assessment #1 has at least one evidence item for every critical category (Monitoring, DR, Access, Integrations, SLA).
- Test data: seeded assessment #1 (see app/seed_data.sql)
- Steps:
  1. Open assessment #1 detail page.
  2. Read the readiness view.
- Expected result: Readiness view shows "No critical information missing" (ready = True).

## TC-003 — Negative: missing owner blocks evidence registration
- Linked REQ/US: REQ-001 / US-001
- Type: Integration
- Priority: High
- Preconditions: Assessment #1 exists.
- Test data: category=SLA, source="Contract PDF", owner="" (empty), freshness_date=2026-06-01, criticality=Critical
- Steps:
  1. Open assessment #1 detail page.
  2. Fill the form leaving "owner" empty.
  3. Submit the form.
- Expected result: Evidence is NOT saved; the browser/server rejects the submission for missing a required field.

## TC-004 — Negative: assessment with missing critical evidence is detected as incomplete
- Linked REQ/US: REQ-003 / US-002
- Type: Integration
- Priority: High
- Preconditions: Assessment #2 exists, missing DR and Integrations evidence (seeded).
- Test data: seeded assessment #2 (see app/seed_data.sql)
- Steps:
  1. Open assessment #2 detail page.
  2. Read the readiness view.
- Expected result: Readiness view lists "DR" and "Integrations" as missing critical categories; assessment shown as not ready.

## TC-005 — Boundary: evidence exactly at the 90-day threshold is NOT stale
- Linked REQ/US: REQ-004
- Type: Unit
- Priority: Medium
- Preconditions: None (pure function test).
- Test data: freshness_date = reference_date - 90 days
- Steps:
  1. Call `is_stale(freshness_date, reference_date)`.
- Expected result: Returns False (not stale) — 90 days is still within the allowed freshness period.

## TC-006 — Boundary: evidence at 91 days IS flagged as stale
- Linked REQ/US: REQ-004
- Type: Unit
- Priority: Medium
- Preconditions: None (pure function test).
- Test data: freshness_date = reference_date - 91 days
- Steps:
  1. Call `is_stale(freshness_date, reference_date)`.
- Expected result: Returns True (stale). Per the change request, this must NOT block submission — only flag it.

## TC-007 — NFR validation: core actions respond within 1 second (pilot scale)
- Linked REQ/US: REQ-008
- Type: System
- Priority: Medium
- Preconditions: SQLite DB seeded with pilot-scale data (2 assessments, ~8 evidence records).
- Test data: seed_data.sql
- Steps:
  1. Measure wall-clock time for GET /assessment/1.
  2. Measure wall-clock time for POST /assessment/1/evidence.
- Expected result: Both operations complete in under 1 second locally.

## TC-008 — Role/security: Contributor cannot submit final assessment
- Linked REQ/US: REQ-005, REQ-009 / US-004
- Type: Integration
- Priority: High
- Preconditions: User "bruno.contrib" exists with role Contributor; assessment #1 is complete (ready).
- Test data: username=bruno.contrib
- Steps:
  1. Open assessment #1 detail page.
  2. Enter "bruno.contrib" in the submit form and submit.
- Expected result: Submission is denied with an "unauthorized role" message; assessment status remains "draft".

## TC-009 — Role/security: Transition Lead can submit when ready
- Linked REQ/US: REQ-005, REQ-006 / US-004
- Type: Integration
- Priority: High
- Preconditions: User "alice.lead" exists with role TransitionLead; assessment #1 is complete (ready).
- Test data: username=alice.lead
- Steps:
  1. Open assessment #1 detail page.
  2. Enter "alice.lead" in the submit form and submit.
- Expected result: Submission succeeds; assessment status becomes "submitted", submitted_by="alice.lead", submitted_at populated.

*(9 test cases delivered — exceeds the minimum of 8 — covering: 2 happy path [TC-001, TC-002], 2 negative [TC-003, TC-004], 2 boundary/validation [TC-005, TC-006], 1 NFR [TC-007], 2 role/security [TC-008, TC-009].)*

## TC-010 — Happy path: Transition Lead raises a valid RFC (added by change request)
- Linked REQ/US: REQ-012 / US-006
- Type: Integration
- Priority: High
- Preconditions: User "alice.lead" exists with role TransitionLead; assessment #1 exists.
- Test data: username=alice.lead, title="Access review gap", question="Who owns the quarterly access review?", assigned_to=bruno.contrib
- Steps:
  1. Open assessment #1 detail page.
  2. Fill and submit the "Raise a new RFC" form with the test data above.
- Expected result: A new RFC is persisted with status "open", raised_by="alice.lead", assigned_to="bruno.contrib".

## TC-011 — Negative: Contributor cannot raise an RFC (added by change request)
- Linked REQ/US: REQ-012 / US-006
- Type: Integration
- Priority: High
- Preconditions: User "bruno.contrib" exists with role Contributor.
- Test data: username=bruno.contrib, title="Test", question="Why?"
- Steps:
  1. Submit the "Raise a new RFC" form as bruno.contrib.
- Expected result: RFC is NOT created; system shows "unauthorized role (only TransitionLead can raise an RFC)".

## TC-012 — Boundary/validation: RFC cannot be answered with empty text (added by change request)
- Linked REQ/US: REQ-013 / US-007
- Type: Unit
- Priority: Medium
- Preconditions: An open RFC exists (seeded RFC #1).
- Test data: answer_text = "" (or whitespace-only)
- Steps:
  1. Call `rfc_rules.answer_rfc(role="Contributor", current_status="open", answer_text="   ")`.
- Expected result: Returns `{success: False, reason: "empty_answer"}`; RFC remains "open" in the database.

## TC-013 — Role/security: only Contributor/TransitionLead can answer an RFC (added by change request)
- Linked REQ/US: REQ-013 / US-007
- Type: Integration
- Priority: High
- Preconditions: User "diana.security" exists with role SecurityOfficer; an open RFC exists (seeded RFC #1).
- Test data: username=diana.security, rfc_id=1, answer_text="an attempted answer"
- Steps:
  1. Submit the "Answer an RFC" form as diana.security.
- Expected result: Answer is NOT saved; system shows "unauthorized role (only Contributor or TransitionLead can answer)"; RFC remains "open".

*(Change request update: 4 new test cases added [TC-010 to TC-013], exceeding the CR's minimum requirement of updating 2 test cases. Total test case count is now 13.)*

## BDD / Gherkin

See `bdd/features/readiness.feature` for the executable-style Feature with 4 scenarios (happy path, missing evidence, unauthorized user, stale-evidence flag).

**Change request update:** see `bdd/features/rfc.feature` (new file) for the RFC tool Feature with 4 scenarios (happy path, missing required fields, unauthorized raise, unauthorized answer), satisfying the CR's requirement to update at least 1 BDD scenario.

## Definition of Done

### DoD — Requirement
A requirement is done when:
1. It has a unique ID, type (Functional/Non-functional/Constraint), priority, and is linked to at least one Objective and one CSF.
2. It has explicit, testable Acceptance Criteria and a stated validation method.
3. It has at least one corresponding test case or automated test that exercises its acceptance criteria, and it appears in the traceability matrix.

### DoD — User Story
A user story is done when:
1. It follows the "As a / I want / so that" format and is linked to at least one requirement.
2. It has explicit Acceptance Criteria.
3. The behaviour it describes is implemented in the app (or explicitly deferred and documented, as with US-002b) and is covered by at least one test case or BDD scenario.

### DoD — Final Delivery
The final delivery is done when:
1. All 14 documentation deliverables exist in `docs/`, each with at least one dedicated Git commit.
2. The app runs locally per the instructions in README.md and demonstrably implements the rules listed in `docs/11_vibe_coding_app.md`.
3. All automated tests pass against the reproducible SQLite test data, the traceability matrix is coherent with every other artefact, and the change request has been fully processed and reflected across requirements, tests, data architecture and decision log.
