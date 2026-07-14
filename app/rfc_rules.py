"""
rfc_rules.py

Business logic for the RFC (Request for Comment) tool, added by the change request
described in docs/09_change_request.md.

The RFC tool lets a Transition Lead request additional transition information from a
Contributor, in a structured, documented way (title + question -> answer), rather than
an ad-hoc chat message. Answered RFCs can be flagged as FAQ candidates for future
AMS transitions (REQ-013).

Kept free of Flask/SQLite specifics, like readiness_rules.py, so it is directly
unit-testable and reusable by both the app and the automated tests.
"""

ROLE_ALLOWED_TO_RAISE = "TransitionLead"
ROLES_ALLOWED_TO_ANSWER = ("Contributor", "TransitionLead")


def can_raise_rfc(role):
    """REQ-012 AC-1: only TransitionLead may raise a new RFC."""
    return role == ROLE_ALLOWED_TO_RAISE


def can_answer_rfc(role):
    """REQ-013 AC-2: only Contributor or TransitionLead may answer an RFC."""
    return role in ROLES_ALLOWED_TO_ANSWER


def validate_new_rfc(title, question):
    """REQ-012 AC-2: title and question are both mandatory."""
    return bool(title and title.strip()) and bool(question and question.strip())


def raise_rfc(role, title, question):
    """
    Attempts to raise a new RFC.
    Returns { success: bool, reason: str|None }.
    Does not touch the database - the caller persists the row if success is True.
    """
    if not can_raise_rfc(role):
        return {"success": False, "reason": "unauthorized_role"}
    if not validate_new_rfc(title, question):
        return {"success": False, "reason": "missing_required_fields"}
    return {"success": True, "reason": None}


def answer_rfc(role, current_status, answer_text):
    """
    Attempts to answer an existing RFC.
    Returns { success: bool, reason: str|None }.
    REQ-013 AC-1: answer_text must be non-empty.
    REQ-013 AC-2: role must be Contributor or TransitionLead.
    An already-answered RFC cannot be answered again in this pilot (kept simple: single Q&A).
    """
    if not can_answer_rfc(role):
        return {"success": False, "reason": "unauthorized_role"}
    if current_status == "answered":
        return {"success": False, "reason": "already_answered"}
    if not answer_text or not answer_text.strip():
        return {"success": False, "reason": "empty_answer"}
    return {"success": True, "reason": None}
