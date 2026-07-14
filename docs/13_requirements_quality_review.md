# Requirements Quality Review

Each of the 10+ structured requirements from `docs/02_objectives_csfs_requirements.md` is reviewed against 7 quality dimensions: **Clear, Testable, Atomic, Feasible, Traceable, Not implementation-specific, Aligned with scope**.

## Review table

| REQ | Clear | Testable | Atomic | Feasible | Traceable | Not impl-specific | Aligned with scope | Issue found? |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | Yes | Yes | Yes | Yes | Yes (OBJ-02/CSF-02) | Yes | Yes | None |
| REQ-002 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | None |
| REQ-003 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | None |
| REQ-004 | Partially (original draft) | Yes | Yes | Yes | Yes | Yes | Yes | **Issue Q-001**: original wording didn't specify the boundary behaviour at exactly 90 days — fixed (see below) |
| REQ-005 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | None (clarified further by change request, not a quality defect) |
| REQ-006 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | None |
| REQ-007 | Yes | Partially | Yes | Yes | Yes | Yes | Yes | **Issue Q-002**: AC-2 ("clicking opens detail view") is more of a UI interaction test than a business rule test — borderline testable, kept as Demo-validated |
| REQ-008 | Partially | Partially | Yes | Yes (for pilot scale) | Yes | Yes | Yes | **Issue Q-003**: "under 1 second" has no defined measurement method/tooling in the original acceptance criteria — fixed (see below) |
| REQ-009 | Yes | Yes | **No** (originally bundled two ideas) | Yes | Yes | Yes | Yes | **Issue Q-004**: originally combined "role must exist" and "checks happen server-side" into one AC — split for atomicity (see below) |
| REQ-010 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | None |
| REQ-011 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | None |

**4 real quality issues identified** (Q-001 through Q-004), satisfying the minimum of 4.

## Corrected requirements

### Correction 1 — REQ-004 (Clear / Testable)
- **Before:** "The system must flag any evidence item whose freshness date is older than 90 days as stale."
- **Problem:** Does not state what happens at exactly 90 days — ambiguous boundary, which would make AT-003's parametrized test impossible to write unambiguously.
- **After:** "The system must flag any evidence item whose freshness date is **more than** 90 days old as stale (evidence exactly 90 days old is **not** flagged); flagging does not block submission."
- **Why it is better:** The boundary is now explicit and directly testable — this exact wording is what `AT-003`'s parametrized test (`90 → False`, `91 → True`) verifies.

### Correction 2 — REQ-008 (Testable)
- **Before:** "The system must respond quickly for core intake actions."
- **Problem:** No threshold, no measurement method — essentially a restatement of the original poor requirement R1 ("fast").
- **After:** "For pilot data volume (≤ tens of assessments, ≤ hundreds of evidence items), core actions (view assessment, add evidence, submit) must complete in under 1 second on local SQLite persistence, measured via TC-007 wall-clock timing."
- **Why it is better:** Adds a concrete threshold, a defined data scale, and a named validation method (TC-007), making the requirement independently verifiable instead of subjective.

### Correction 3 — REQ-009 (Atomic)
- **Before AC:** "AC-1: Role checks are enforced and cannot be bypassed by an unrecognized or missing user."
- **Problem:** Bundles two distinct testable conditions (unrecognized username vs. server-side enforcement location) into a single AC, making it unclear which specific test satisfies which half.
- **After:**
  - "AC-1: A username not present in the UserRole table cannot submit an assessment."
  - "AC-2: Role checks happen server-side (in the Flask route), not only in client-side UI logic."
- **Why it is better:** Each AC is now independently verifiable — AC-1 by a data-driven test (unknown username), AC-2 by code review of `main.py` (the check exists in the route handler, not only conditionally rendered in HTML), matching the DoD requirement that each AC maps to a specific validation method.

## Addendum — quality check on requirements added by the change request

REQ-012 and REQ-013 (RFC tool) were added after this review was first performed, as part of processing the change request (see `docs/09_change_request.md`). A quick pass against the same 7 dimensions: both are Clear, Testable (AC-1/AC-2 map directly to AT-005..AT-008), Atomic (raising vs. answering were deliberately split into two separate requirements rather than one bundled "RFC" requirement — this atomicity was a lesson learned directly from Correction 3 above), Feasible, Traceable (linked to OBJ-01/CSF-01 and OBJ-02/CSF-02 respectively), Not implementation-specific (they describe the raise/answer capability and its constraints, not the Flask routes or SQLite table used to build it), and Aligned with scope (they extend, not conflict with, the existing role model). No new quality issues were found in REQ-012/REQ-013 at the time of writing.

## Reflection
The quality review surfaced a pattern: most defects were in the *acceptance criteria*, not in the requirement statement itself — the requirement sounded reasonable in prose, but its AC didn't yet constrain it enough to be unambiguously testable. This mirrors exactly the diagnosis-phase finding (P-012: "none of R1–R10 defines how the requirement would be verified"), which reinforces why acceptance criteria and validation method were made mandatory fields for every requirement in `docs/02`.
