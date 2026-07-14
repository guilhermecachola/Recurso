# User Stories

## US-001 — Register evidence with mandatory metadata

As a Contributor,
I want to register an evidence item with source, owner and freshness date,
so that readiness claims for my assessment are backed by traceable proof.

- Linked requirement(s): REQ-001, REQ-002
- Acceptance Criteria:
  - AC-1: I cannot save an evidence item without source, owner and freshness date.
  - AC-2: I can pick a category from a fixed list (Monitoring, DR, Access, Integrations, SLA) and a criticality (Critical/Important/Optional).

## US-002 — See what critical information is missing

As a Transition Lead,
I want to see which critical categories have no evidence at all,
so that I know exactly what to chase before the transition can be considered ready.

- Linked requirement(s): REQ-003
- Acceptance Criteria:
  - AC-1: When I open an assessment, missing critical categories are listed explicitly.
  - AC-2: When no critical category is missing, the assessment is shown as "ready".

## US-003 — Be warned about outdated evidence without being blocked

As a Service Owner,
I want evidence older than 90 days to be flagged as stale,
so that I know it may need refreshing, without that alone preventing the transition from moving forward.

- Linked requirement(s): REQ-004
- Acceptance Criteria:
  - AC-1: Evidence older than 90 days shows a visible "STALE" flag.
  - AC-2: Stale evidence does not, by itself, block submission of the assessment.

## US-004 — Restrict final submission to the Transition Lead

As a Security Officer,
I want only the Transition Lead role to be able to submit a final assessment,
so that readiness decisions are made by an accountable, approved role.

- Linked requirement(s): REQ-005, REQ-009
- Acceptance Criteria:
  - AC-1: A Contributor attempting to submit gets a clear rejection message and the assessment stays in draft.
  - AC-2: A Transition Lead can submit only when no critical category is missing.

## US-005 — View a consolidated readiness summary

As a Client Manager,
I want a single summary screen listing every assessment and its readiness state,
so that I can quickly understand overall transition health without opening each assessment individually.

- Linked requirement(s): REQ-007
- Acceptance Criteria:
  - AC-1: The summary page lists every assessment with name, status and readiness (ready / missing information).
  - AC-2: I can click through from the summary into the full evidence detail of any assessment.

## US-006 — Raise an RFC to request missing information (added by change request)

As a Transition Lead,
I want to raise a structured RFC (title + question) on an assessment, optionally addressed to a specific Contributor,
so that missing or unclear transition information gets formally requested and documented instead of chased informally over chat.

- Linked requirement(s): REQ-012
- Acceptance Criteria:
  - AC-1: I can raise an RFC with a title and question tied to an assessment, optionally assigned to a Contributor.
  - AC-2: I cannot raise an RFC unless I am recognized as TransitionLead; the system rejects the attempt otherwise.

## US-007 — Answer an RFC as documented knowledge (added by change request)

As a Contributor,
I want to answer an open RFC with a structured response,
so that my knowledge becomes documented and reusable — potentially as a future AMS FAQ — rather than lost in an informal conversation.

- Linked requirement(s): REQ-013
- Acceptance Criteria:
  - AC-1: I can submit an answer to an open RFC and it becomes visible as "answered", with my username recorded as the answerer.
  - AC-2: I cannot submit an empty answer, and I cannot answer an RFC that has already been answered.

*(Change request note: the CR explicitly required updating at least 1 user story; both US-006 and US-007 are added here since they are the two natural sides — raise / answer — of the same RFC workflow required by REQ-012/REQ-013.)*

## Story split

### Original story
US-002 — "As a Transition Lead, I want to see readiness status and act on it, so that I know what to do next."

### Split into
- US-002: See which critical categories have no evidence at all (read-only detection/visibility).
- US-002b: Receive a recommended next action per missing category (e.g., "chase DR evidence from Security Officer") — deferred, not implemented in this pilot slice.

### Justification
The original story mixed two different concerns with very different complexity: (1) *detecting and displaying* missing information, which is a well-defined, testable rule (compare evidence categories against the fixed critical list), and (2) *recommending actions*, which requires additional business rules about ownership/escalation paths that were not confirmed by any stakeholder (raw notes only say "Transition Lead: We need a summary... and recommendations for the first 90 days", without specifying the recommendation logic). Splitting isolates the testable, in-scope part (US-002) from the exploratory, out-of-scope-for-this-pilot part (US-002b), so the team can deliver and test US-002 with confidence while US-002b is properly scoped later. This decision is also recorded in the Decision Log (DEC-004).
