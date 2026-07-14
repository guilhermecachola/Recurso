# Objectives, CSFs and Requirements

## Product Objectives

- **OBJ-01** — Improve readiness visibility for AMS transition stakeholders, so that gaps in monitoring, DR, access and SLA documentation are known before day 1 of AMS operation.
- **OBJ-02** — Establish evidence-based governance over the transition, so that every readiness claim (e.g. "monitoring is documented") is backed by a traceable, owned, dated artefact rather than a verbal statement.
- **OBJ-03** — Control who can change the official readiness position, so that only accountable roles can move an assessment from draft to a submitted, actionable status.

## Critical Success Factors

- **CSF-01** — Critical AMS transition information (monitoring, DR, access, integrations, SLA) is complete, current and evidence-backed. *(supports OBJ-01, OBJ-02)*
- **CSF-02** — Every piece of evidence used to support readiness is traceable to a source, an owner and a freshness date. *(supports OBJ-02)*
- **CSF-03** — Only authorized roles (Transition Lead) can submit a final readiness assessment; Contributors can prepare but not finalize. *(supports OBJ-03)*

## Structured requirements

### REQ-001 — Capture evidence with source, owner and freshness date
- Type: Functional
- Stakeholder: Transition Lead, Contributor
- Priority: High
- Description: The system must allow a Contributor or Transition Lead to register an evidence item for a readiness category, capturing at minimum its source, owner and freshness date.
- Linked objective: OBJ-02
- Linked CSF: CSF-02
- Acceptance Criteria:
  - AC-1: An evidence item cannot be saved without source, owner and freshness date filled in.
  - AC-2: Saved evidence is associated with exactly one assessment and one readiness category.
- Validation method: Test (AT-001, AT-002), Demo

### REQ-002 — Classify evidence by readiness category and criticality
- Type: Functional
- Stakeholder: Transition Lead
- Priority: High
- Description: Each evidence item must be tagged with a readiness category (Monitoring, DR, Access, Integrations, SLA) and a criticality level (Critical, Important, Optional).
- Linked objective: OBJ-01
- Linked CSF: CSF-01
- Acceptance Criteria:
  - AC-1: The category field only accepts values from the fixed list of readiness categories.
  - AC-2: The criticality field only accepts Critical, Important or Optional.
- Validation method: Test, Review

### REQ-003 — Detect and display missing critical information
- Type: Functional
- Stakeholder: Transition Lead, Client Manager
- Priority: High
- Description: The system must compare the evidence registered for an assessment against the fixed list of critical readiness categories and clearly display which critical categories have no evidence at all.
- Linked objective: OBJ-01
- Linked CSF: CSF-01
- Acceptance Criteria:
  - AC-1: If any critical category has zero evidence items, the assessment is shown as "not ready" with the missing categories listed.
  - AC-2: If all critical categories have at least one evidence item, the assessment is shown as "ready".
- Validation method: Test (AT-001, AT-002), Demo

### REQ-004 — Flag stale evidence based on freshness date
- Type: Functional
- Stakeholder: Ops Engineer, Service Owner
- Priority: High
- Description: The system must flag any evidence item whose freshness date is older than 90 days as "stale", without blocking submission (updated by change request, see docs/09_change_request.md).
- Linked objective: OBJ-01
- Linked CSF: CSF-01
- Acceptance Criteria:
  - AC-1: Evidence with freshness_date exactly 90 days old is NOT flagged as stale.
  - AC-2: Evidence with freshness_date 91+ days old IS flagged as stale, but the assessment can still be submitted.
- Validation method: Test (AT-003)

### REQ-005 — Restrict final submission to the Transition Lead role
- Type: Functional
- Stakeholder: Security Officer
- Priority: High
- Description: Only a user with the "Transition Lead" role may submit (finalize) a readiness assessment. Contributors may create and edit draft evidence but cannot submit.
- Linked objective: OBJ-03
- Linked CSF: CSF-03
- Acceptance Criteria:
  - AC-1: A submission attempt by a Contributor is rejected with a clear message and the assessment remains in "draft".
  - AC-2: A submission attempt by a Transition Lead succeeds only if no critical category is missing.
- Validation method: Test (AT-004), Demo

### REQ-006 — Persist assessment status (draft / submitted)
- Type: Functional
- Stakeholder: Transition Lead
- Priority: Medium
- Description: The system must persist each assessment's lifecycle status (draft or submitted), along with who submitted it and when.
- Linked objective: OBJ-03
- Linked CSF: CSF-03
- Acceptance Criteria:
  - AC-1: A newly created assessment starts in "draft" status.
  - AC-2: After a successful submission, status changes to "submitted" and submitted_by/submitted_at are recorded.
- Validation method: Test (AT-004)

### REQ-007 — Provide a readiness summary view for managers
- Type: Functional
- Stakeholder: Transition Lead, Client Manager
- Priority: Medium
- Description: The system must provide a summary screen listing all assessments, their status and their readiness (ready / missing information), so managers can quickly see overall transition health.
- Linked objective: OBJ-01
- Linked CSF: CSF-01
- Acceptance Criteria:
  - AC-1: The summary lists every assessment with its current readiness state.
  - AC-2: Clicking an assessment opens its detailed evidence and missing-information view.
- Validation method: Demo, Review

### REQ-008 — Response time for core intake actions
- Type: Non-functional
- Stakeholder: Client Manager
- Priority: Medium
- Description: For the pilot data volume (tens of assessments, hundreds of evidence items), core actions (view assessment, add evidence, submit) must complete in under 1 second on local SQLite persistence.
- Linked objective: OBJ-01
- Linked CSF: CSF-01
- Acceptance Criteria:
  - AC-1: Measured local response time for "add evidence" is under 1 second for pilot-scale data.
  - AC-2: Measured local response time for "view assessment readiness" is under 1 second for pilot-scale data.
- Validation method: Measurement

### REQ-009 — Role-based access control
- Type: Non-functional
- Stakeholder: Security Officer
- Priority: High
- Description: The system must enforce that evidence-editing and submission actions are always checked against a defined role (Transition Lead, AMS Manager, Contributor, Security Officer) before being executed, with no action available to an unauthenticated/unrecognized user.
- Linked objective: OBJ-03
- Linked CSF: CSF-03
- Acceptance Criteria:
  - AC-1: A username not present in the UserRole table cannot submit an assessment.
  - AC-2: Role checks happen server-side, not only in the UI.
- Validation method: Test (AT-004), Review

### REQ-010 — Auditability of evidence and submissions
- Type: Non-functional
- Stakeholder: Security Officer
- Priority: Medium
- Description: Every evidence item and every submission event must be traceable to a created_at/submitted_at timestamp and an owning user, supporting later audit of the transition record.
- Linked objective: OBJ-02
- Linked CSF: CSF-02
- Acceptance Criteria:
  - AC-1: Every evidence record stores created_at and owner.
  - AC-2: Every submitted assessment stores submitted_by and submitted_at.
- Validation method: Review, Test

### REQ-011 — Persistence constraint (business rule)
- Type: Constraint
- Stakeholder: Developer, Transition Lead
- Priority: High
- Description: For this exercise, persistence must use SQLite (or JSON, if justified) only — no external database services — to keep the pilot simple, reproducible and easy to reset between demonstrations and tests.
- Linked objective: OBJ-01, OBJ-02, OBJ-03
- Linked CSF: CSF-01, CSF-02, CSF-03
- Acceptance Criteria:
  - AC-1: The app and the automated tests both run against a SQLite file that can be recreated from schema.sql + seed_data.sql.
  - AC-2: No cloud/external database dependency is required to run the app or the tests locally.
- Validation method: Review, Demo

*(Note: 10 requirements were required at minimum; REQ-001 to REQ-011 are provided — 11 — to keep FR/NFR/constraint coverage balanced and to have one spare for traceability robustness. REQ-001, 002, 003, 004, 005, 006, 007 = 7 Functional; REQ-008, 009, 010 = 3 Non-functional; REQ-011 = 1 Constraint.)*

### REQ-012 — Raise an RFC to request missing information (added by change request)
- Type: Functional
- Stakeholder: Transition Lead, Contributor
- Priority: High
- Description: The system must allow a Transition Lead to raise a structured RFC (title + question) on a specific assessment, optionally assigned to a specific Contributor, to formally request additional transition information instead of chasing it informally over chat.
- Linked objective: OBJ-01
- Linked CSF: CSF-01
- Acceptance Criteria:
  - AC-1: Only a user with role TransitionLead can raise a new RFC; a Contributor's (or any other role's) attempt is rejected with `unauthorized_role`.
  - AC-2: An RFC cannot be created without both a title and a question filled in.
- Validation method: Test (AT-005, AT-006)

### REQ-013 — Answer and document RFCs as structured transition knowledge (added by change request)
- Type: Functional
- Stakeholder: Contributor, Transition Lead
- Priority: High
- Description: The system must allow a Contributor (or Transition Lead) to answer an open RFC with a structured answer, which is persisted as documented transition knowledge and can be flagged as an FAQ candidate to help build future AMS documentation, addressing the raw-notes problem of scattered/undocumented knowledge.
- Linked objective: OBJ-02
- Linked CSF: CSF-02
- Acceptance Criteria:
  - AC-1: An RFC cannot be marked "answered" without non-empty answer text, and an already-answered RFC cannot be answered again.
  - AC-2: A user with a role other than Contributor or TransitionLead (e.g. SecurityOfficer, AMSManager) cannot answer an RFC.
- Validation method: Test (AT-007, AT-008)

*(Change request update: REQ-012 and REQ-013 were added on top of the original REQ-001–REQ-011 set, bringing the total to 13 requirements — 9 Functional, 3 Non-functional, 1 Constraint. See docs/09_change_request.md for the full impact analysis.)*

## Rewrite of initial poor requirements

| Original | Problem | Rewritten version | Justification |
|---|---|---|---|
| R1: The system must be fast | Not measurable, no threshold | REQ-008: Core intake actions (view, add evidence, submit) complete in under 1 second for pilot-scale data on local SQLite | Adds a concrete, testable threshold and defines the actions and data scale it applies to |
| R4: Create a dashboard | Solution mixed into the requirement | REQ-007: Provide a readiness summary view listing all assessments, their status and readiness state | States the business outcome (visibility of readiness) instead of prescribing a specific UI artifact |
| R5: Use AI to generate recommendations | Solution/technology mixed into the requirement, no acceptance criteria | REQ-003: Detect and display missing critical information per assessment | Focuses on the actual business need (surface gaps) rather than mandating a specific technology; a recommendation engine can be layered later once the core detection logic is validated |
| R6: The app must allow evidence | No acceptance criteria, "evidence" undefined | REQ-001: Capture evidence with source, owner and freshness date (mandatory fields) | Defines exactly what "evidence" means structurally and how it will be validated |
| R8: Use Microsoft authentication | Solution mixed into requirement, conflicts with pilot timeline/scope | REQ-009: Enforce role-based access control server-side for all editing/submission actions (implementation may start with a simplified role lookup for the pilot, real SSO deferred — see Decision Log DEC-003) | Separates the real need (role-based control) from a specific identity-provider choice not yet confirmed as available/necessary for the pilot |
