# Change Request Impact

> **Process note (Git):** per the exam rules, this change request may only be considered valid if it is processed *after* a commit that establishes the traceability matrix baseline. When you commit this repository, make sure your commit history shows something like `D7 Add traceability matrix baseline` *before* `D9 Apply change request and update impacted artefacts` — do not squash them together, and do not backdate commits to fake this order; do it for real, in that sequence.
>
> **Revision note:** an earlier draft of this document used the illustrative example change request printed in the exam statement itself (Security Officer role clarification + evidence staleness) as a placeholder, since the real instructor-issued change request had not been received yet at that point. That placeholder's *effects* are still valid and remain implemented in the system (REQ-004's "flag, not reject" rule and REQ-005's Transition-Lead-only submission rule — see Decision Log DEC-005), but this document now reflects the **actual change request received from the instructor**, reproduced below, which is the one that counts for grading.

## Change request received

```
Regra importante sobre quando aplicar o Change Request
Este Change Request só deve ser considerado após o commit da D7 — Traceability Matrix.

Novo Requisito — Ferramenta RFC
O Transition Lead necessita de uma ferramenta de RFC (Request for Comment) para
solicitar informação adicional aos Contributors relativamente a qualquer intake.

A ferramenta RFC não deve ser tratada apenas como um chat ou como um simples pedido
de esclarecimento. Deve também permitir documentar conhecimento relevante da
transição e poderá contribuir para a criação de futuras FAQs no contexto AMS.

Em resumo, a ferramenta RFC deverá funcionar de forma semelhante às RFCs usadas em
contextos de normalização técnica, ajudando a criar documentação técnica estruturada
e a evitar as lacunas de documentação que contribuíram para a situação atual da
transição.
```

## Impact analysis

| Artefact | Impact | Updated? |
|---|---|---|
| Requirements | Added REQ-012 (raise an RFC, Transition-Lead-only, title+question mandatory) and REQ-013 (answer an RFC as Contributor/Transition-Lead, non-empty answer, FAQ-candidate flag) in `docs/02_objectives_csfs_requirements.md`, linked to OBJ-01/CSF-01 and OBJ-02/CSF-02 respectively | Yes |
| Use Cases | Added UC-007 "Raise and answer an RFC" in `docs/04_use_cases.md`, with its own main flow, 2 alternative flows and 2 exceptions; updated the actor descriptions in the Use Case diagram section | Yes |
| User Stories | Added US-006 (raise) and US-007 (answer) in `docs/05_user_stories.md`, each with 2 acceptance criteria, linked to REQ-012/REQ-013 | Yes |
| Test Cases | Added TC-010 (happy path raise), TC-011 (negative — Contributor cannot raise), TC-012 (boundary — empty answer rejected), TC-013 (role/security — SecurityOfficer cannot answer) in `docs/06_tests_validation.md` | Yes (4, exceeds minimum of 2) |
| BDD Scenarios | Added new file `bdd/features/rfc.feature` with 4 scenarios (happy path, missing required fields, unauthorized raise, unauthorized answer) | Yes |
| Traceability Matrix | Added 2 new rows (REQ-012, REQ-013) to `docs/07_traceability_matrix.md`, each mapping through UC-007/US-006 or US-007 to their test cases, BDD scenarios, the new RFC data entity, and AT-005..AT-008 | Yes |
| Decision Log | Added DEC-008 (single Q&A pair, not full thread/separate FAQ table), DEC-009 (role restrictions: TransitionLead raises, Contributor/TransitionLead answer), DEC-010 (RFC kept independent from Evidence) in `docs/08_decision_log.md` | Yes |
| Data Architecture | Added the `RFC` entity (new `rfc` table: title, question, raised_by, assigned_to, status, answer_text, answered_by, is_faq_candidate, timestamps) to `docs/10_data_architecture.md`, including relationships to Assessment, UserRole and ReadinessQuestion, and a new validation-rules block | Yes — schema change required (new table, `app/schema.sql`) |
| Test Database / Test Data | `app/seed_data.sql` extended with 3 RFC records: one open+assigned, one already-answered+FAQ-candidate, one open+unassigned, covering valid and edge cases | Yes |
| Automated Tests | Added new file `tests/test_rfc_database.py` with 8 tests (AT-005 happy path, AT-006 negative ×2, AT-007 boundary ×2, AT-008 role/security ×3), all running against the same reproducible SQLite pattern as the existing suite | Yes (8, exceeds minimum of 1) |

## Summary of functional change

The RFC tool is a genuinely new capability, not a clarification of an existing rule, so — unlike the illustrative staleness/role change request handled earlier — it required an actual schema change (new `rfc` table) rather than just tightened wording. Three design questions had to be resolved before implementation, all recorded in the Decision Log:

1. **How "structured" should the RFC be, given it must not be "just a chat"?** Resolved as a single title + question → single answer pair (not a full message thread), which is enough to force documentation discipline (a title and a specific question, not a freeform conversation) without over-building a threading feature the CR didn't ask for. See DEC-008.

2. **Who can raise/answer?** The CR explicitly frames this as "Transition Lead requests information from Contributors," so `raise_rfc()` is gated to `TransitionLead` only, and `answer_rfc()` is gated to `Contributor` or `TransitionLead` (self-answering allowed, but SecurityOfficer/AMSManager cannot answer in this pilot). This mirrors the existing least-privilege pattern already established for assessment submission (REQ-005/REQ-009), keeping the security model consistent across the app rather than inventing a new one. See DEC-009.

3. **How does this connect to "future FAQs"?** Rather than building a separate FAQ page/entity (out of scope for a one-week pilot), an `is_faq_candidate` boolean was added directly to the `rfc` table, letting a Transition Lead flag a resolved RFC as reusable knowledge. This is a deliberately minimal hook that satisfies the CR's wording ("poderá contribuir para a criação de futuras FAQs") without overbuilding. See DEC-010.

The change was verified end-to-end, not just at the unit-test level: the running Flask app was smoke-tested via curl for all four flows (unauthorized raise rejected, authorized raise accepted, unauthorized answer rejected, authorized answer accepted and persisted), in addition to the 8 new pytest tests in `tests/test_rfc_database.py` — see `evidence/test_results.md` for the full automated-test output.
