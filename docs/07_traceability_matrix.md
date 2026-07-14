# Traceability Matrix

> **Baseline commit:** the version of this matrix without the REQ-012/REQ-013 rows below is the traceability baseline (`D7 Add traceability matrix baseline`), committed before the change request was processed, per the exam's Git process rule. The two RFC-related rows were added afterward as part of `D9 Apply change request and update impacted artefacts`.

| Objective | CSF | Requirement | Use Case | User Story | Acceptance Criteria | Test Case / BDD Scenario | Data Entity / Model | Automated Test |
|---|---|---|---|---|---|---|---|---|
| OBJ-02 | CSF-02 | REQ-001 | UC-001 | US-001 | AC-1, AC-2 | TC-001, TC-003 / — | Evidence | AT-001 (indirectly, via seeded evidence), AT-002 |
| OBJ-01 | CSF-01 | REQ-002 | UC-001 | US-001 | AC-1, AC-2 | TC-001 | Evidence, ReadinessQuestion | AT-001 |
| OBJ-01 | CSF-01 | REQ-003 | UC-002, UC-004 (via UC-005 include) | US-002 | AC-1, AC-2 | TC-002, TC-004 / Scenario: Happy path, Scenario: Missing evidence | Evidence, ReadinessQuestion, Assessment | AT-001, AT-002 |
| OBJ-01 | CSF-01 | REQ-004 | UC-002, UC-003 (extend) | US-003 | AC-1, AC-2 | TC-005, TC-006 / Scenario: Stale evidence is flagged | Evidence | AT-003 |
| OBJ-03 | CSF-03 | REQ-005 | UC-004 | US-004 | AC-1, AC-2 | TC-008, TC-009 / Scenario: Unauthorized user, Scenario: Happy path | Assessment, UserRole | AT-004 |
| OBJ-03 | CSF-03 | REQ-006 | UC-004 | US-004 | AC-1, AC-2 | TC-009 | Assessment | AT-004 |
| OBJ-01 | CSF-01 | REQ-007 | UC-006 | US-005 | AC-1, AC-2 | TC-002, TC-004 (readiness state reused in summary) | Assessment, Evidence | AT-001, AT-002 |
| OBJ-01 | CSF-01 | REQ-008 | UC-001, UC-002 | — (NFR, no dedicated story) | AC-1, AC-2 | TC-007 | Evidence, Assessment | — (measured manually, not in pytest suite; see docs/12) |
| OBJ-03 | CSF-03 | REQ-009 | UC-004 | US-004 | AC-1, AC-2 | TC-008 / Scenario: Unauthorized user | UserRole | AT-004 |
| OBJ-02 | CSF-02 | REQ-010 | UC-001, UC-004 | US-001 (partially) | AC-1, AC-2 | TC-001, TC-009 | Evidence, Assessment | AT-004 (submitted_by/at persisted) |
| OBJ-01, OBJ-02, OBJ-03 | CSF-01, CSF-02, CSF-03 | REQ-011 | — (cross-cutting constraint) | — | AC-1, AC-2 | — (validated by all AT-* running against SQLite) | all entities | AT-001..AT-004 (all use SQLite) |
| OBJ-01 | CSF-01 | REQ-012 *(added by CR)* | UC-007 | US-006 | AC-1, AC-2 | TC-010, TC-011 / rfc.feature: Happy path, Missing required fields, Unauthorized user (raise) | RFC | AT-005, AT-006 |
| OBJ-02 | CSF-02 | REQ-013 *(added by CR)* | UC-007 | US-007 | AC-1, AC-2 | TC-012, TC-013 / rfc.feature: Happy path, Unauthorized user (answer) | RFC | AT-007, AT-008 |

## Traceability chain

- Objective: **OBJ-03** — Control who can change the official readiness position, so that only accountable roles can move an assessment from draft to a final, submitted status.
- CSF: **CSF-03** — Only authorized roles (Transition Lead) can submit a final readiness assessment; Contributors can prepare but not finalize.
- Requirement: **REQ-005** — Restrict final submission to the Transition Lead role.
- Use Case / User Story: **UC-004 — Submit final readiness assessment** / **US-004 — Restrict final submission to the Transition Lead**.
- Acceptance Criteria: AC-1 (a Contributor's submission attempt is rejected and the assessment stays in draft), AC-2 (a Transition Lead's submission succeeds only if no critical category is missing).
- Test Case / BDD Scenario: **TC-008** (Contributor cannot submit), **TC-009** (Transition Lead can submit when ready) / Gherkin **"Unauthorized user — Contributor cannot submit final assessment"**.
- Automated Test: **AT-004** family — `test_at004_role_contributor_cannot_submit`, `test_at004_role_transition_lead_can_submit_when_ready`, `test_at004_role_transition_lead_blocked_if_evidence_missing` (tests/test_readiness_database.py).
- Data Entity / Model: **Assessment** (status, submitted_by, submitted_at) and **UserRole** (username, role) — `app/schema.sql`.

### Explanation

**Why the requirement supports the objective:** OBJ-03 is only achieved if the system actually *enforces* who can finalize a transition assessment — otherwise "controlling who can change the readiness position" is just a policy statement with no teeth. REQ-005 turns that policy into a concrete, checkable rule (role must equal `TransitionLead`) that the application evaluates on every submission attempt, server-side, not just hidden in the UI. This directly operationalizes CSF-03.

**Why the test validates the requirement:** AT-004's three tests exercise both halves of REQ-005's acceptance criteria against real database-backed data: `test_at004_role_contributor_cannot_submit` loads the seeded Contributor user (`bruno.contrib`) from the `user_role` table and asserts the submission function returns `unauthorized_role`; `test_at004_role_transition_lead_can_submit_when_ready` loads the seeded Transition Lead (`alice.lead`) against a *complete* assessment and asserts success, then re-reads the `assessment` row from SQLite to confirm `status`/`submitted_by` were actually persisted (not just returned in memory); `test_at004_role_transition_lead_blocked_if_evidence_missing` confirms that even the correct role is blocked when critical evidence is missing, tying REQ-005 to REQ-003 as the tests intentionally interact.

**What would be affected if the requirement changed:** If REQ-005 changed (e.g., "AMS Manager may also submit"), the impact would cascade through: `readiness_rules.can_submit()` (the `ROLE_ALLOWED_TO_SUBMIT` constant or logic), the `user_role` CHECK constraint/seed data (no schema change needed, but new test users would be required), UC-004's main flow description, US-004's acceptance criteria, TC-008/TC-009, the Gherkin "Unauthorized user" scenario (whose actor set would need re-checking), all three AT-004 tests (at least one would need a new positive-case test for the newly authorized role), and this traceability matrix row. This is exactly the kind of change the mid-week change request exercised in practice (see `docs/09_change_request.md`), where the DR/evidence-freshness rule — not the role rule — was clarified, but the same ripple pattern applies to any change touching REQ-005.
