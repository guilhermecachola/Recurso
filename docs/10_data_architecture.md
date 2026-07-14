# Data Architecture

## Persistence option
- SQLite / JSON: **SQLite**, via Python's standard `sqlite3` module (no ORM/framework).
- Justification: SQLite gives real relational constraints (FOREIGN KEY, CHECK, UNIQUE) that let the schema itself enforce part of the business rules (e.g. valid role values, valid criticality values), and lets both the app and the automated tests share one reproducible, file-based `schema.sql` + `seed_data.sql` pair, satisfying REQ-011. JSON was considered but rejected because the Assessment↔Evidence relationship and role lookups are naturally relational, and SQLite adds negligible setup cost for a one-week pilot (see Decision Log DEC-001).

## Data model overview

| Entity / Model | Purpose | Related requirements |
|---|---|---|
| Assessment | Represents one readiness assessment (a transition scope) and its lifecycle status | REQ-003, REQ-005, REQ-006, REQ-007 |
| Evidence | A single proof item (source, owner, freshness date, category, criticality) linked to an Assessment | REQ-001, REQ-002, REQ-004, REQ-010 |
| ReadinessQuestion | The fixed list of critical readiness categories used to detect missing information | REQ-002, REQ-003 |
| UserRole | Maps a username to a role, used for submission authorization | REQ-005, REQ-009, REQ-010 |
| RFC *(added by change request)* | A structured request-for-comment raised by a Transition Lead and answered by a Contributor, capturing documented transition knowledge and optional FAQ candidacy | REQ-012, REQ-013 |

## Entity details

### Assessment (table `assessment`)

| Field | Type | Required? | Notes |
|---|---|---:|---|
| id | integer | Yes | Primary key, autoincrement |
| name | text | Yes | Human-readable label, e.g. "OrderCare - EU Region Transition" |
| status | text | Yes | `draft` (default) or `submitted` — CHECK constraint |
| created_at | text (ISO datetime) | Yes | Defaults to `datetime('now')` |
| submitted_by | text | No | FK to `user_role.username`; set only on successful submission |
| submitted_at | text (ISO datetime) | No | Set only on successful submission |

### Evidence (table `evidence`)

| Field | Type | Required? | Notes |
|---|---|---:|---|
| id | integer | Yes | Primary key, autoincrement |
| assessment_id | integer | Yes | FK to `assessment.id` |
| category | text | Yes | FK to `readiness_question.category` |
| source | text | Yes | e.g. "DR test report Q2" |
| owner | text | Yes | Person/role accountable for this evidence |
| freshness_date | text (ISO date, `YYYY-MM-DD`) | Yes | Used to compute staleness (REQ-004) |
| criticality | text | Yes | `Critical` / `Important` / `Optional` — CHECK constraint |
| created_at | text (ISO datetime) | Yes | Defaults to `datetime('now')` |

### ReadinessQuestion (table `readiness_question`)

| Field | Type | Required? | Notes |
|---|---|---:|---|
| id | integer | Yes | Primary key, autoincrement |
| category | text | Yes | Unique — e.g. "Monitoring", "DR", "Access", "Integrations", "SLA" |
| question_text | text | Yes | e.g. "Is the DR procedure documented with recent test evidence?" |
| is_critical | integer (0/1) | Yes | All 5 seeded categories are critical (`1`) in this pilot |

### UserRole (table `user_role`)

| Field | Type | Required? | Notes |
|---|---|---:|---|
| id | integer | Yes | Primary key, autoincrement |
| username | text | Yes | Unique |
| role | text | Yes | `TransitionLead` / `AMSManager` / `Contributor` / `SecurityOfficer` — CHECK constraint |

### RFC *(added by change request — table `rfc`)*

| Field | Type | Required? | Notes |
|---|---|---:|---|
| id | integer | Yes | Primary key, autoincrement |
| assessment_id | integer | Yes | FK to `assessment.id` |
| category | text | No | Optional FK to `readiness_question.category` |
| title | text | Yes | Short label for the RFC |
| question | text | Yes | The information being requested |
| raised_by | text | Yes | FK to `user_role.username`; must resolve to role `TransitionLead` |
| assigned_to | text | No | FK to `user_role.username`; expected `Contributor`, optional (unassigned RFCs are allowed) |
| status | text | Yes | `open` (default) or `answered` — CHECK constraint |
| answer_text | text | No | Populated only once answered |
| answered_by | text | No | FK to `user_role.username`; populated only once answered |
| is_faq_candidate | integer (0/1) | Yes | Default 0; manually flagged once an answer is judged reusable as future AMS documentation |
| created_at | text (ISO datetime) | Yes | Defaults to `datetime('now')` |
| answered_at | text (ISO datetime) | No | Populated only once answered |

## Relationships

| Source entity | Relationship | Target entity |
|---|---|---|
| Assessment | has many | Evidence |
| Evidence | belongs to (by value) | ReadinessQuestion (via `category`) |
| Assessment | submitted by (optional) | UserRole (via `submitted_by` → `username`) |
| Assessment | has many *(CR)* | RFC |
| RFC | raised by *(CR)* | UserRole (via `raised_by` → `username`, must be TransitionLead) |
| RFC | assigned to (optional) *(CR)* | UserRole (via `assigned_to` → `username`, expected Contributor) |
| RFC | belongs to (by value, optional) *(CR)* | ReadinessQuestion (via `category`) |

## Validation rules supported

| Rule | Related REQ | Implemented in app? | Tested by |
|---|---|---|---|
| Evidence source, owner, freshness_date are mandatory | REQ-001 | Yes (`schema.sql` NOT NULL + `main.py` form validation) | TC-001, TC-003 |
| Evidence category must be one of the fixed readiness categories | REQ-002 | Yes (FK to `readiness_question.category`) | TC-001; implicitly all AT-* since they read seeded categories |
| Evidence criticality must be Critical/Important/Optional | REQ-002 | Yes (CHECK constraint in `schema.sql`) | TC-001 |
| Evidence older than 90 days is FLAGGED, not rejected | REQ-004 | Yes (`readiness_rules.is_stale()`, pure function, no DB flag stored) | AT-003 |
| Assessment is "ready" only if every critical category has evidence | REQ-003 | Yes (`readiness_rules.assessment_readiness()`) | AT-001, AT-002 |
| Only role `TransitionLead` may submit an assessment | REQ-005, REQ-009 | Yes (`readiness_rules.can_submit()`, enforced server-side in `main.py`) | AT-004 |
| Submission requires role AND no missing critical evidence | REQ-005, REQ-003 | Yes (`readiness_rules.submit_assessment()`) | AT-004 |

| Only role `TransitionLead` may raise an RFC | REQ-012 | Yes (`rfc_rules.can_raise_rfc()`) | AT-006 |
| An RFC requires both title and question to be created | REQ-012 | Yes (`rfc_rules.validate_new_rfc()`) | AT-006 |
| An RFC cannot be answered with empty text, or answered twice | REQ-013 | Yes (`rfc_rules.answer_rfc()`) | AT-007 |
| Only `Contributor` or `TransitionLead` may answer an RFC | REQ-013 | Yes (`rfc_rules.can_answer_rfc()`) | AT-008 |

## Note on the original change request (staleness — see docs/09_change_request.md history)
The first change request processed resolved an ambiguity in REQ-004: no schema change was required, since staleness is intentionally **not** a stored column (e.g. no `is_stale BOOLEAN` field) — it is a derived value computed on read from `freshness_date`, which keeps the flag always accurate relative to "today" instead of going stale itself. This design choice is recorded in Decision Log DEC-005.

## Note on the RFC tool change request (see docs/09_change_request.md)
This change request DID require a schema change: a new `rfc` table was added (see "RFC" entity above), plus its CRUD helpers in `app/database.py` and its own business-rule module `app/rfc_rules.py`. No existing table was modified, and no existing test or seed row needed to change — `app/seed_data.sql` was only extended with 3 new RFC records (one open unassigned, one open assigned, one already answered and flagged as an FAQ candidate) to give the automated tests (AT-005 to AT-008) both valid and invalid/edge cases to exercise. See Decision Log DEC-008 to DEC-010 for the specific modeling choices made.
