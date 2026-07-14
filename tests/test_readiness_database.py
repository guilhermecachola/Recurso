"""
tests/test_readiness_database.py

Automated database-backed tests for the AMS Transition Intake & Readiness Assessment app.
Uses a dedicated, reproducible SQLite test database (created fresh from schema.sql +
seed_data.sql for every test run) - never touches app/readiness.db used for manual demo.

Covers:
  AT-001  Happy path            - REQ-004 / REQ-007  (complete assessment recognized as ready)
  AT-002  Negative               - REQ-007            (assessment with missing critical evidence)
  AT-003  Boundary / validation  - REQ-004             (evidence freshness: 90d boundary)
  AT-004  Role / security        - REQ-008             (only TransitionLead can submit)

Run with:  pytest -v  (from repository root, with app/ on PYTHONPATH - see pytest.ini)
"""

import os
import sys
import sqlite3
from datetime import date, timedelta

import pytest

APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
sys.path.insert(0, os.path.abspath(APP_DIR))

import database as db  # noqa: E402
import readiness_rules as rules  # noqa: E402

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_readiness.db")


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
# AT-001 - Happy path: complete assessment loaded from DB is recognized as ready
# ---------------------------------------------------------------------------
def test_at001_happy_path_complete_assessment_is_ready(conn):
    critical = db.get_critical_categories(conn)
    evidence = db.get_evidence_for_assessment(conn, assessment_id=1)  # seeded as complete

    readiness = rules.assessment_readiness(evidence, critical, reference_date=date(2026, 7, 10))

    assert readiness["ready"] is True
    assert readiness["missing"] == []


# ---------------------------------------------------------------------------
# AT-002 - Negative: assessment with missing critical evidence is detected as incomplete
# ---------------------------------------------------------------------------
def test_at002_negative_missing_critical_evidence_detected(conn):
    critical = db.get_critical_categories(conn)
    evidence = db.get_evidence_for_assessment(conn, assessment_id=2)  # seeded missing DR + Integrations

    readiness = rules.assessment_readiness(evidence, critical, reference_date=date(2026, 7, 10))

    assert readiness["ready"] is False
    assert "DR" in readiness["missing"]
    assert "Integrations" in readiness["missing"]


# ---------------------------------------------------------------------------
# AT-003 - Boundary/validation: evidence exactly at / just over / just under the
# 90-day freshness threshold is flagged correctly (not rejected, only flagged).
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "age_days, expected_stale",
    [
        (90, False),   # exactly at threshold -> NOT stale (allowed period)
        (91, True),    # just over threshold -> stale
        (30, False),   # well within period -> not stale
    ],
)
def test_at003_boundary_evidence_freshness_threshold(age_days, expected_stale):
    reference_date = date(2026, 7, 10)
    freshness_date = (reference_date - timedelta(days=age_days)).isoformat()

    result = rules.is_stale(freshness_date, reference_date=reference_date)

    assert result is expected_stale


def test_at003_boundary_uses_real_seeded_stale_record(conn):
    """Cross-check the boundary rule against a real DB record (assessment 2, Monitoring evidence,
    seeded far outside the 90-day window)."""
    evidence = db.get_evidence_for_assessment(conn, assessment_id=2)
    monitoring = next(e for e in evidence if e["category"] == "Monitoring")

    assert rules.is_stale(monitoring["freshness_date"], reference_date=date(2026, 7, 10)) is True


# ---------------------------------------------------------------------------
# AT-004 - Role/security: Contributor cannot submit; TransitionLead can submit
# when validation rules are satisfied (REQ-008, updated by the change request)
# ---------------------------------------------------------------------------
def test_at004_role_contributor_cannot_submit(conn):
    role = db.get_user_role(conn, "bruno.contrib")  # seeded as Contributor
    critical = db.get_critical_categories(conn)
    evidence = db.get_evidence_for_assessment(conn, assessment_id=1)

    result = rules.submit_assessment(role, evidence, critical, reference_date=date(2026, 7, 10))

    assert result["success"] is False
    assert result["reason"] == "unauthorized_role"


def test_at004_role_transition_lead_can_submit_when_ready(conn):
    role = db.get_user_role(conn, "alice.lead")  # seeded as TransitionLead
    critical = db.get_critical_categories(conn)
    evidence = db.get_evidence_for_assessment(conn, assessment_id=1)  # complete assessment

    result = rules.submit_assessment(role, evidence, critical, reference_date=date(2026, 7, 10))

    assert result["success"] is True

    # Confirm the submission is actually persisted in the database (DB-backed behaviour)
    db.mark_submitted(conn, assessment_id=1, username="alice.lead")
    updated = db.get_assessment(conn, 1)
    assert updated["status"] == "submitted"
    assert updated["submitted_by"] == "alice.lead"


def test_at004_role_transition_lead_blocked_if_evidence_missing(conn):
    """Even the correct role cannot submit an assessment that is missing critical evidence."""
    role = db.get_user_role(conn, "alice.lead")
    critical = db.get_critical_categories(conn)
    evidence = db.get_evidence_for_assessment(conn, assessment_id=2)  # incomplete assessment

    result = rules.submit_assessment(role, evidence, critical, reference_date=date(2026, 7, 10))

    assert result["success"] is False
    assert result["reason"] == "missing_critical_evidence"
