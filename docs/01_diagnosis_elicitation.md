# Diagnosis and Elicitation

## Problems identified

| ID | Source | Problem | Why it is a problem |
|---|---|---|---|
| P-001 | R1 "The system must be fast" | Not measurable | No threshold, no context (which operation? under what load?) |
| P-002 | R2 "Users need to add project data" | Too broad / ambiguous | "project data" is undefined — which entity, which fields, which validation? |
| P-003 | R3 "The system should be secure" | Non-functional requirement not measurable | "Secure" has no defined control (auth method, role model, audit trail) |
| P-004 | R4 "Create a dashboard" | Requirement mixed with implementation/solution | Describes a UI artifact instead of the underlying business need it should satisfy |
| P-005 | R5 "Use AI to generate recommendations" | Requirement mixed with implementation/solution | Prescribes a technology (AI) instead of stating the outcome needed (e.g., "surface missing critical info and suggested actions") |
| P-006 | R6 "The app must allow evidence" | No acceptance criteria | Does not say what evidence consists of (source, owner, freshness — only revealed later in constraints) |
| P-007 | R8 "Use Microsoft authentication" | Requirement mixed with implementation/solution, and conflicts with scope | Prescribes a specific identity provider before any requirement defines the actual access-control need; also not confirmed as available for a one-week AMS pilot |
| P-008 | R9 "The system should support risk scoring" | Missing acceptance criteria / undefined algorithm | No definition of what inputs feed a "risk score" or what the output scale means |
| P-009 | R10 "It should be user-friendly" | Not measurable, no test method | Subjective; cannot be verified by inspection or test |
| P-010 | Raw notes (Security Officer) vs (Client Manager "fast, next week") | Conflict / unresolved dependency | Strict role-based control (security) vs. a one-week delivery pressure (speed) is a scope/priority conflict that has not been resolved by any stakeholder |
| P-011 | Raw notes (Ops Engineer: "I don't know if alerts are still valid") | Missing stakeholder / missing decision authority | No requirement states who is responsible for validating monitoring evidence freshness |
| P-012 | Whole requirements list | Missing acceptance criteria across the board | None of R1–R10 defines how the requirement would be verified (review, test, demo, measurement) |

## Elicitation questions

| ID | Topic | Question | Target stakeholder |
|---|---|---|---|
| Q-001 | Business | What decision will the readiness assessment output actually drive in the first 90 days (go/no-go, staffing, escalation)? | Client Manager |
| Q-002 | Business | Is the intake meant to cover a single application (OrderCare) or is it expected to be reused for future AMS transitions? | Client Manager / Transition Lead |
| Q-003 | AMS operation | Who is the accountable owner for each monitoring dashboard once AMS takes over? | Ops Engineer |
| Q-004 | AMS operation | What counts as "documented" for monitoring, DR and access procedures — a wiki page, a signed document, a runbook section? | Service Owner |
| Q-005 | Evidence | What evidence formats must be supported (files, links, text notes) in this first version? | Transition Lead / Developer |
| Q-006 | Evidence | Besides source, owner and freshness date, is a criticality or category tag required per evidence item? | Transition Lead |
| Q-007 | Evidence | What is the acceptable freshness window before evidence is considered stale? | Service Owner / Security Officer |
| Q-008 | Security | Which roles exist, and what exactly can each role do (create, edit, submit, approve)? | Security Officer |
| Q-009 | Security | Is authentication in scope for this first version, or is a simple role selection acceptable for the pilot? | Security Officer / Developer |
| Q-010 | Risk/continuity | What inputs should feed the "readiness/risk view" (missing evidence count? stale evidence? category weighting?) | Transition Lead / Service Owner |
| Q-011 | Risk/continuity | Is there a required minimum evidence set (e.g., DR, Monitoring, Access, Integrations, SLA) that must always be present before an assessment can be submitted? | Transition Lead |
| Q-012 | Reporting | Who consumes the "missing critical information" report, and how often (real time, daily, on demand)? | Transition Lead / Client Manager |
| Q-013 | Reporting | Should the readiness view be per-country/per-region or a single consolidated view for OrderCare? | Client Manager |
| Q-014 | Testing/validation | How will "the system must be fast" be validated for a pilot with a handful of users — is a specific response time acceptable? | Developer |
| Q-015 | Testing/validation | What is an acceptable way to demonstrate DR evidence validity given "no evidence" currently exists? | Service Owner / Security Officer |

## Assumptions

| ID | Assumption | Risk if wrong | How to validate |
|---|---|---|---|
| A-001 | Scope is limited to OrderCare's transition intake only, not a multi-application AMS platform | Over-engineering the data model / wasted effort building multi-app scope | Confirm with Client Manager; re-check against "Case constraints — Scope" |
| A-002 | Evidence freshness threshold is 90 days unless the client specifies otherwise | Stale evidence detection could be too strict or too lenient for the real business need | Confirm with Service Owner / Security Officer during the interview follow-up |
| A-003 | Authentication for the pilot is simulated via a role field (username → role lookup), not real Microsoft/AAD SSO | Rejected by Security Officer as insufficient for production, requiring rework | Explicitly flagged as a pilot-only simplification in the Decision Log; validate with Security Officer before go-live |
| A-004 | "Only approved AMS leads should change readiness assessments" means only the `TransitionLead` role may submit/finalize an assessment; `Contributor` may still edit drafts | Wrong role model could block legitimate users or allow unauthorized submissions | Confirm exact role list and permissions matrix with Security Officer |
| A-005 | Stale evidence should be flagged as a risk indicator but must NOT block submission (business impact if it did: transitions could never be submitted while any old dashboard exists) | If wrong, submitted assessments could hide real staleness risk, or legitimate transitions could get blocked indefinitely | Confirmed explicitly by the mid-week change request (see docs/09_change_request.md) |
| A-006 | The 5 critical readiness categories are: Monitoring, DR, Access, Integrations, SLA (derived directly from the interview notes) | Missing a category the client actually considers critical (e.g., "escalation contacts") | Review category list with Transition Lead before final submission |
| A-007 | "Fast" (R1) can be operationalized, for this pilot, as page responses under ~1 second on local SQLite with pilot-scale data volume | Client may have a stricter/different performance expectation for production scale | Confirm acceptable response time with Client Manager; treat as pilot-only NFR |
| A-008 | Persistence for this exercise is SQLite (single file), acceptable for a pilot/prototype, not multi-region production data | A real multi-country deployment would need a shared/replicated database, which is out of scope here | Explicitly scoped as a prototype in docs/11_vibe_coding_app.md |
