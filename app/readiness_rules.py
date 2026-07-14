"""
readiness_rules.py

Core business logic for the AMS Transition Intake & Readiness Assessment app.
Kept free of Flask/SQLite specifics so it can be unit-tested directly and
reused by both the web app (main.py) and the automated tests.

Implements:
- REQ-004 Evidence freshness rule (evidence older than STALE_THRESHOLD_DAYS is FLAGGED, not rejected)
- REQ-007 Missing critical information detection
- REQ-008 Role-based submission control (only TransitionLead may submit)
"""

from datetime import date, datetime

STALE_THRESHOLD_DAYS = 90
ROLE_ALLOWED_TO_SUBMIT = "TransitionLead"


def _parse_date(value):
    """Accept either a date object or an ISO 'YYYY-MM-DD' string."""
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def is_stale(freshness_date, reference_date=None, threshold_days=STALE_THRESHOLD_DAYS):
    """
    Returns True if evidence is older than `threshold_days` relative to `reference_date`.
    Per the change request: stale evidence is FLAGGED, never auto-rejected.
    """
    freshness_date = _parse_date(freshness_date)
    reference_date = reference_date or date.today()
    if isinstance(reference_date, str):
        reference_date = _parse_date(reference_date)
    age_days = (reference_date - freshness_date).days
    return age_days > threshold_days


def missing_critical_categories(evidence_list, critical_categories):
    """
    evidence_list: list of dicts with at least a 'category' key.
    critical_categories: list of category names considered critical (from ReadinessQuestion).
    Returns the list of critical categories that have NO evidence at all.
    """
    present = {e["category"] for e in evidence_list}
    return [c for c in critical_categories if c not in present]


def stale_evidence_items(evidence_list, reference_date=None):
    """Returns the subset of evidence_list whose freshness_date is stale."""
    return [e for e in evidence_list if is_stale(e["freshness_date"], reference_date)]


def assessment_readiness(evidence_list, critical_categories, reference_date=None):
    """
    Aggregates the readiness view for an assessment.
    Returns a dict: { ready: bool, missing: [...], stale: [...] }
    'ready' means no missing critical categories (stale evidence does not block readiness,
    it is only flagged as a risk per the change request).
    """
    missing = missing_critical_categories(evidence_list, critical_categories)
    stale = stale_evidence_items(evidence_list, reference_date)
    return {
        "ready": len(missing) == 0,
        "missing": missing,
        "stale": stale,
    }


def can_submit(role):
    """
    REQ-008 (updated by change request): only TransitionLead can submit the
    final assessment. Contributors may edit/create draft evidence but not submit.
    """
    return role == ROLE_ALLOWED_TO_SUBMIT


def submit_assessment(role, evidence_list, critical_categories, reference_date=None):
    """
    Attempts to submit an assessment.
    Returns a dict: { success: bool, reason: str|None, missing: [...] }
    Submission requires BOTH: correct role AND no missing critical evidence.
    """
    if not can_submit(role):
        return {"success": False, "reason": "unauthorized_role", "missing": []}

    readiness = assessment_readiness(evidence_list, critical_categories, reference_date)
    if not readiness["ready"]:
        return {"success": False, "reason": "missing_critical_evidence", "missing": readiness["missing"]}

    return {"success": True, "reason": None, "missing": []}
