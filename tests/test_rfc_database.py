"""
tests/test_rfc_database.py

Automated database-backed tests for the RFC (Request for Comment) tool,
added by the change request described in docs/09_change_request.md.

Uses the same reproducible SQLite test database pattern as
tests/test_readiness_database.py (fresh DB from schema.sql + seed_data.sql
per test run).

Covers:
  AT-005  Happy path            - REQ-012  (TransitionLead raises a valid RFC)
  AT-006  Negative               - REQ-012  (Contributor cannot raise an RFC)
  AT-007  Boundary / validation  - REQ-013  (RFC cannot be answered with empty text)
  AT-008  Role / security        - REQ-013  (only Contributor/TransitionLead can answer;
                                              an answered RFC can be flagged as FAQ candidate)
"""

import os
import sys

import pytest

APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
sys.path.insert(0, os.path.abspath(APP_DIR))

import database as db  # noqa: E402
import rfc_rules  # noqa: E402

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_rfc.db")


@pytest.fixture()
def conn():
    """Creates a fresh, reproducible SQLite test database for every test."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db.init_db(db_path=TEST_DB_PATH, seed=True)
    connection = db.get_connection(TEST_DB_PATH)
    yield connection
    connection.close()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


# ---------------------------------------------------------------------------
# AT-005 - Happy path: TransitionLead raises a valid RFC and it is persisted
# ---------------------------------------------------------------------------
def test_at005_happy_path_transition_lead_raises_rfc(conn):
    role = db.get_user_role(conn, "alice.lead")  # seeded as TransitionLead

    result = rfc_rules.raise_rfc(role, "Access review gap", "Who owns the quarterly access review?")

    assert result["success"] is True

    new_id = db.create_rfc(
        conn, assessment_id=1, category="Access",
        title="Access review gap", question="Who owns the quarterly access review?",
        raised_by="alice.lead", assigned_to="bruno.contrib",
    )
    stored = db.get_rfc(conn, new_id)
    assert stored["status"] == "open"
    assert stored["raised_by"] == "alice.lead"
    assert stored["assigned_to"] == "bruno.contrib"


# ---------------------------------------------------------------------------
# AT-006 - Negative: Contributor cannot raise an RFC
# ---------------------------------------------------------------------------
def test_at006_negative_contributor_cannot_raise_rfc(conn):
    role = db.get_user_role(conn, "bruno.contrib")  # seeded as Contributor

    result = rfc_rules.raise_rfc(role, "Some title", "Some question")

    assert result["success"] is False
    assert result["reason"] == "unauthorized_role"


def test_at006_negative_missing_title_or_question_rejected(conn):
    role = db.get_user_role(conn, "alice.lead")  # correct role, but incomplete fields

    result_missing_title = rfc_rules.raise_rfc(role, "", "A question without a title")
    result_missing_question = rfc_rules.raise_rfc(role, "A title without a question", "")

    assert result_missing_title["success"] is False
    assert result_missing_title["reason"] == "missing_required_fields"
    assert result_missing_question["success"] is False
    assert result_missing_question["reason"] == "missing_required_fields"


# ---------------------------------------------------------------------------
# AT-007 - Boundary / validation: an RFC cannot be marked answered with empty text
# ---------------------------------------------------------------------------
def test_at007_boundary_empty_answer_rejected(conn):
    role = db.get_user_role(conn, "bruno.contrib")
    open_rfc = db.get_rfc(conn, 1)  # seeded as 'open'
    assert open_rfc["status"] == "open"

    result = rfc_rules.answer_rfc(role, open_rfc["status"], "   ")  # whitespace-only

    assert result["success"] is False
    assert result["reason"] == "empty_answer"


def test_at007_boundary_already_answered_rfc_cannot_be_answered_again(conn):
    role = db.get_user_role(conn, "bruno.contrib")
    answered_rfc = db.get_rfc(conn, 2)  # seeded as already 'answered'
    assert answered_rfc["status"] == "answered"

    result = rfc_rules.answer_rfc(role, answered_rfc["status"], "a new answer attempt")

    assert result["success"] is False
    assert result["reason"] == "already_answered"


# ---------------------------------------------------------------------------
# AT-008 - Role/security: only Contributor/TransitionLead can answer;
# a successful answer is persisted and can be flagged as an FAQ candidate.
# ---------------------------------------------------------------------------
def test_at008_role_security_officer_cannot_answer_rfc(conn):
    role = db.get_user_role(conn, "diana.security")  # seeded as SecurityOfficer
    open_rfc = db.get_rfc(conn, 1)

    result = rfc_rules.answer_rfc(role, open_rfc["status"], "an attempted answer")

    assert result["success"] is False
    assert result["reason"] == "unauthorized_role"


def test_at008_role_contributor_can_answer_and_result_is_persisted(conn):
    role = db.get_user_role(conn, "bruno.contrib")
    open_rfc = db.get_rfc(conn, 1)

    result = rfc_rules.answer_rfc(role, open_rfc["status"], "DR test was run in May, report attached.")
    assert result["success"] is True

    db.answer_rfc_record(conn, rfc_id=1, answer_text="DR test was run in May, report attached.", answered_by="bruno.contrib")
    updated = db.get_rfc(conn, 1)

    assert updated["status"] == "answered"
    assert updated["answered_by"] == "bruno.contrib"
    assert updated["answer_text"] == "DR test was run in May, report attached."


def test_at008_answered_rfc_can_be_flagged_as_faq_candidate(conn):
    """Confirms REQ-013's link to future FAQ documentation: an answered RFC can be
    promoted to an FAQ candidate, and this is persisted in the database."""
    rfc_already_answered = db.get_rfc(conn, 2)  # seeded already answered, is_faq_candidate=1
    assert rfc_already_answered["is_faq_candidate"] == 1

    # And confirm the flag can be toggled on a different (also-answered) record via the helper
    db.answer_rfc_record(conn, rfc_id=1, answer_text="Some answer", answered_by="bruno.contrib")
    db.set_faq_candidate(conn, rfc_id=1, is_faq_candidate=True)
    updated = db.get_rfc(conn, 1)
    assert updated["is_faq_candidate"] == 1
