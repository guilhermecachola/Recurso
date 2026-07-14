# Use Cases

## Use Case Diagram

```
Actors: Contributor, Transition Lead, Security Officer   (AMS Manager is a 4th actor, view-only — see note)

                        AMS Transition Intake & Readiness Assessment
                       +----------------------------------------------+
                       |                                                |
 (Contributor) ------->| UC-001 Register evidence item                 |
      |                |                                                |
      |                | UC-002 View assessment readiness status       |<---- (Transition Lead)
      |                |          (<<include>> UC-005 Detect missing   |         |
      |                |           critical information)               |         |
      |                |                                                |         |
      |                | UC-003 Flag stale evidence                    |         |
      |                |          (<<extend>> of UC-002)                |         |
      |                |                                                |         |
      |                | UC-004 Submit final readiness assessment      |<--------+
      |                |          (<<include>> UC-005 Detect missing   |
      |                |           critical information)               |
      |                |                                                |
      |                | UC-006 View readiness summary (all assessments)|<---- (Transition Lead)
      |                |                                                |
      +--------------->| UC-005 Detect missing critical information    |
                        |         (shared/included logic)               |
                        |                                                |
                        +----------------------------------------------+
                                          ^
                                          |
                            (Security Officer) -- defines/audits roles,
                                                   is notified on submission
```

Actors:
- **Contributor** — registers/edits draft evidence; answers RFCs raised by a Transition Lead.
- **Transition Lead** — everything a Contributor can do, plus submits the final assessment and raises RFCs (UC-007, added by change request).
- **Security Officer** — defines role assignments and audits who can act; consumes traceability of evidence, submissions and RFCs (does not directly edit evidence or answer RFCs in this slice).

*(Change request update: UC-007 "Raise and answer an RFC" was added to this diagram's use case set; it does not `<<include>>` UC-005 since RFC completeness has its own independent validation in `rfc_rules.py`, separate from evidence-category detection.)*

`<<include>>` relationships: UC-002 (view readiness) and UC-004 (submit) both include UC-005 (detect missing critical information), since both need the same missing-category calculation.
`<<extend>>` relationship: UC-003 (flag stale evidence) extends UC-002, since staleness flags are shown as part of viewing readiness but represent an optional extension point (an assessment can be viewed even with zero evidence, in which case there's nothing to flag as stale).

## UC-001 — Register evidence item

- Primary actor: Contributor (also usable by Transition Lead)
- Goal: Add a new piece of evidence (source, owner, freshness date, category, criticality) to a draft assessment.
- Preconditions: The assessment exists and is in "draft" status. The actor is a recognized user (Contributor or Transition Lead).
- Trigger: Actor opens an assessment and fills in the "Add evidence" form.
- Related requirements: REQ-001, REQ-002

### Main flow
1. Actor opens the assessment detail page.
2. Actor selects a readiness category, fills in source, owner, freshness date and criticality.
3. Actor submits the form.
4. System validates that source, owner and freshness date are present and category/criticality are valid values.
5. System stores the evidence item linked to the assessment.
6. System re-renders the assessment page showing the new evidence and the updated readiness view.

### Alternative flows
- AF-1: Actor leaves freshness date empty → system shows a validation error and does not save the record (goes back to step 2).

### Exceptions
- EX-1: Assessment is already "submitted" → system still allows viewing evidence but the business decision is that further edits should not change a submitted historical record (out of scope for this prototype: submitted assessments are not currently locked at the database level; documented as a known limitation, see docs/13 and Decision Log).

### Postconditions
- Success: A new evidence row exists in the `evidence` table linked to the assessment; the readiness view reflects it.
- Failure: No record is created; the user sees a validation message.

## UC-004 — Submit final readiness assessment

- Primary actor: Transition Lead
- Goal: Move an assessment from "draft" to "submitted", making it the official readiness position for that scope.
- Preconditions: The actor is a recognized user. The assessment exists and is currently "draft".
- Trigger: Transition Lead clicks "Submit assessment" and enters their username.
- Related requirements: REQ-003, REQ-005, REQ-006

### Main flow
1. Transition Lead opens the assessment detail page and reviews evidence/readiness view.
2. Transition Lead enters their username and submits the "Submit final assessment" form.
3. System looks up the role for that username.
4. System checks the role is "Transition Lead" (UC-005 include: recompute missing critical categories).
5. System checks there are no missing critical categories.
6. System sets assessment status to "submitted", records submitted_by and submitted_at.
7. System shows the updated (submitted) assessment.

### Alternative flows
- AF-1: A Contributor attempts to submit → system rejects with "role not authorized", assessment stays in draft (see UC main flow step 4 failing).
- AF-2: A Transition Lead attempts to submit while a critical category is missing → system rejects with the list of missing categories, assessment stays in draft (step 5 failing).

### Exceptions
- EX-1: Username does not exist in `user_role` table → treated the same as an unauthorized role (no role found ⇒ cannot submit).

### Postconditions
- Success: `assessment.status = 'submitted'`, `submitted_by` and `submitted_at` populated.
- Failure: `assessment.status` remains `'draft'`, no fields changed, user sees the specific rejection reason (role vs. missing evidence).

## UC-007 — Raise and answer an RFC (added by change request)

- Primary actor: Transition Lead (raises the RFC); Contributor (answers it)
- Goal: Formally request missing or unclear transition information from a Contributor and capture the answer as structured, reusable documentation (potentially an FAQ candidate), instead of an informal chat exchange.
- Preconditions: The assessment exists. The actor raising the RFC is a recognized user with role TransitionLead.
- Trigger: Transition Lead identifies a documentation gap (e.g. missing DR evidence) and opens the "Raise a new RFC" form on the assessment page.
- Related requirements: REQ-012, REQ-013

### Main flow
1. Transition Lead opens the assessment detail page and fills in the "Raise a new RFC" form: username, title, question, optional category, optional assigned Contributor username.
2. System checks the role is TransitionLead and that title and question are both filled in (`<<include>>` UC-005-style validation, mirrored in `rfc_rules.raise_rfc()`).
3. System creates the RFC with status `open`, `raised_by` set to the Transition Lead's username.
4. Contributor (assigned or otherwise) opens the same assessment page, sees the open RFC listed, and fills in the "Answer an RFC" form: RFC id, username, answer text.
5. System checks the role is Contributor or TransitionLead, the RFC is still `open`, and the answer text is not empty.
6. System sets the RFC's status to `answered`, records `answer_text`, `answered_by`, `answered_at`.
7. (Optional, manual) Transition Lead later flags the answered RFC as an FAQ candidate (`is_faq_candidate = 1`) if it is likely to be useful for future AMS transitions.

### Alternative flows
- AF-1: A Contributor attempts to raise an RFC → rejected at step 2 with `unauthorized_role`; no RFC is created.
- AF-2: A SecurityOfficer or AMSManager attempts to answer an RFC → rejected at step 5 with `unauthorized_role`; RFC remains `open`.

### Exceptions
- EX-1: The RFC id given in the answer form does not exist → system shows "RFC not found", no update performed.
- EX-2: An already-`answered` RFC is submitted again for answering → rejected with `already_answered`; the original answer is preserved (single Q&A pair per RFC in this pilot, see Decision Log DEC-008).

### Postconditions
- Success (raise): a new `rfc` row exists with `status = 'open'`.
- Success (answer): the `rfc` row has `status = 'answered'`, `answer_text`, `answered_by`, `answered_at` populated.
- Failure: no `rfc` row is created/updated; the user sees the specific rejection reason.
