# Screenshots / Notes — Vibe Coding App

> Replace this with actual screenshots (drag PNG/JPG files into this folder and reference them below) taken while running the app locally, per `docs/11_vibe_coding_app.md`.

## Note 1 — Home page / summary view
Command: `python main.py`, then open http://127.0.0.1:5000/
Expected: two seeded assessments listed — "OrderCare - EU Region Transition" (Ready) and "OrderCare - LATAM Region Transition" (Missing info).
`[screenshot: home_page.png]`

## Note 2 — Assessment detail with missing critical information
URL: http://127.0.0.1:5000/assessment/2
Expected: "Missing critical categories: DR, Integrations" shown in red; evidence table shows the Monitoring row flagged STALE.
`[screenshot: assessment_2_missing_and_stale.png]`

## Note 3 — Adding evidence
URL: http://127.0.0.1:5000/assessment/2 → fill "Add evidence" form (category=DR, source="DR runbook v2", owner="diana.security", freshness_date=2026-07-01, criticality=Critical) → submit.
Expected: page re-renders, "DR" no longer appears in the missing-categories list (only "Integrations" remains).
`[screenshot: add_evidence_result.png]`

## Note 4 — Role-gated submission
URL: http://127.0.0.1:5000/assessment/1 → "Submit final assessment" form.
- Entering `bruno.contrib` (Contributor) → expect rejection message "role ... is not authorized".
- Entering `alice.lead` (TransitionLead) → expect successful submission, status becomes "submitted".
`[screenshot: submit_denied_contributor.png]`
`[screenshot: submit_success_transition_lead.png]`

## CLI verification actually performed during development (terminal output, not a screenshot)
```
$ curl -s http://127.0.0.1:5000/assessment/2 | grep -o 'Missing critical categories:[^<]*'
Missing critical categories: DR, Integrations
```
This confirms the missing-critical-information flow end-to-end (server rendering the correct computed state), independent of the pytest suite.

## Note 5 — RFC tool (added by change request): raise + answer flow, verified via CLI
```
$ curl -s -X POST http://127.0.0.1:5000/assessment/1/rfc -d "username=bruno.contrib&title=Test&question=Why?"
  | grep -o 'RFC not created:[^<]*'
RFC not created: unauthorized role (only TransitionLead can raise an RFC).

$ curl -s -X POST http://127.0.0.1:5000/assessment/1/rfc \
    -d "username=alice.lead&title=New+RFC&question=Any+update+on+access+review%3F&assigned_to=bruno.contrib" \
    -o /dev/null -w "%{http_code}\n"
302

$ curl -s -X POST http://127.0.0.1:5000/rfc/answer -d "next_assessment_id=2&rfc_id=1&username=diana.security&answer_text=x" \
  | grep -o 'Answer not saved:[^<]*'
Answer not saved: unauthorized role (only Contributor or TransitionLead can answer).

$ curl -s -X POST http://127.0.0.1:5000/rfc/answer \
    -d "next_assessment_id=2&rfc_id=1&username=bruno.contrib&answer_text=Yes,+DR+test+was+run+in+May,+report+attached." \
    -o /dev/null -w "%{http_code}\n"
302

$ curl -s http://127.0.0.1:5000/assessment/2 | grep -o 'answered'
answered
```
This confirms all four RFC business rules end-to-end through the real running app (not just pytest): unauthorized raise rejected, authorized raise accepted, unauthorized answer rejected, authorized answer accepted and persisted.
`[screenshot: rfc_list_and_forms.png]`
`[screenshot: rfc_answered_faq_candidate.png]`
