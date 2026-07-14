"""
database.py

Thin SQLite access layer for the AMS Readiness Intake app.
Schema: schema.sql | Seed data: seed_data.sql
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "readiness.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "seed_data.sql")


def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=DB_PATH, seed=True):
    """(Re)creates the database from schema.sql and, if seed=True, loads seed_data.sql."""
    conn = get_connection(db_path)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    if seed:
        with open(SEED_PATH, "r") as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()


def get_critical_categories(conn):
    rows = conn.execute(
        "SELECT category FROM readiness_question WHERE is_critical = 1"
    ).fetchall()
    return [r["category"] for r in rows]


def get_evidence_for_assessment(conn, assessment_id):
    rows = conn.execute(
        "SELECT * FROM evidence WHERE assessment_id = ?", (assessment_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_assessment(conn, assessment_id):
    row = conn.execute(
        "SELECT * FROM assessment WHERE id = ?", (assessment_id,)
    ).fetchone()
    return dict(row) if row else None


def list_assessments(conn):
    rows = conn.execute("SELECT * FROM assessment ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def get_user_role(conn, username):
    row = conn.execute(
        "SELECT role FROM user_role WHERE username = ?", (username,)
    ).fetchone()
    return row["role"] if row else None


def add_evidence(conn, assessment_id, category, source, owner, freshness_date, criticality):
    conn.execute(
        """INSERT INTO evidence (assessment_id, category, source, owner, freshness_date, criticality)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (assessment_id, category, source, owner, freshness_date, criticality),
    )
    conn.commit()


def mark_submitted(conn, assessment_id, username):
    conn.execute(
        "UPDATE assessment SET status = 'submitted', submitted_by = ?, submitted_at = datetime('now') WHERE id = ?",
        (username, assessment_id),
    )
    conn.commit()


def get_rfcs_for_assessment(conn, assessment_id):
    rows = conn.execute(
        "SELECT * FROM rfc WHERE assessment_id = ? ORDER BY id", (assessment_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_rfc(conn, rfc_id):
    row = conn.execute("SELECT * FROM rfc WHERE id = ?", (rfc_id,)).fetchone()
    return dict(row) if row else None


def create_rfc(conn, assessment_id, category, title, question, raised_by, assigned_to=None):
    cur = conn.execute(
        """INSERT INTO rfc (assessment_id, category, title, question, raised_by, assigned_to)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (assessment_id, category or None, title, question, raised_by, assigned_to or None),
    )
    conn.commit()
    return cur.lastrowid


def answer_rfc_record(conn, rfc_id, answer_text, answered_by):
    conn.execute(
        """UPDATE rfc SET status = 'answered', answer_text = ?, answered_by = ?,
           answered_at = datetime('now') WHERE id = ?""",
        (answer_text, answered_by, rfc_id),
    )
    conn.commit()


def set_faq_candidate(conn, rfc_id, is_faq_candidate=True):
    conn.execute(
        "UPDATE rfc SET is_faq_candidate = ? WHERE id = ?",
        (1 if is_faq_candidate else 0, rfc_id),
    )
    conn.commit()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
