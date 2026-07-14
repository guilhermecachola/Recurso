# Macro / Mezzo / Micro

## Macro

| ID | Capability | Description |
|---|---|---|
| MAC-001 | AMS Readiness Assessment | Ability to determine, at any point, whether an application transition to AMS has all critical operational information in place. |
| MAC-002 | Evidence-based Transition Governance | Ability to back every readiness claim with traceable, owned, dated evidence rather than verbal assurance. |
| MAC-003 | Controlled Assessment Lifecycle | Ability to move an assessment from draft to a final, accountable submitted state, restricted to authorized roles. |

## Mezzo

| ID | Functional area | Related Macro |
|---|---|---|
| MEZ-001 | Capture intake answers / evidence | MAC-001, MAC-002 |
| MEZ-002 | Manage evidence metadata (source, owner, freshness, category, criticality) | MAC-002 |
| MEZ-003 | Identify missing critical information | MAC-001 |
| MEZ-004 | Flag stale evidence | MAC-001, MAC-002 |
| MEZ-005 | Review readiness status (summary view) | MAC-001 |
| MEZ-006 | Control submission by role | MAC-003 |

## Micro

| ID | Rule / Validation | Related Mezzo | Related REQ |
|---|---|---|---|
| MIC-001 | Freshness date is mandatory for every evidence item | MEZ-002 | REQ-001 |
| MIC-002 | Source and owner are mandatory for every evidence item | MEZ-002 | REQ-001 |
| MIC-003 | Category must be one of the 5 fixed readiness categories (Monitoring, DR, Access, Integrations, SLA) | MEZ-001, MEZ-002 | REQ-002 |
| MIC-004 | Criticality must be one of Critical / Important / Optional | MEZ-002 | REQ-002 |
| MIC-005 | Evidence older than 90 days must be flagged as stale (not rejected) | MEZ-004 | REQ-004 |
| MIC-006 | An assessment is "ready" only if every critical category has at least one evidence item | MEZ-003 | REQ-003 |
| MIC-007 | Only the "Transition Lead" role can submit (finalize) an assessment | MEZ-006 | REQ-005 |
| MIC-008 | A submission is blocked if any critical category is still missing, even for a Transition Lead | MEZ-006, MEZ-003 | REQ-005 |
