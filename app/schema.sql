-- AMS Transition Intake & Readiness Assessment
-- Schema aligned with docs/10_data_architecture.md

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS rfc;
DROP TABLE IF EXISTS evidence;
DROP TABLE IF EXISTS assessment;
DROP TABLE IF EXISTS readiness_question;
DROP TABLE IF EXISTS user_role;

-- UserRole: who can do what (REQ-008 role control)
CREATE TABLE user_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('TransitionLead', 'AMSManager', 'Contributor', 'SecurityOfficer'))
);

-- ReadinessQuestion: fixed list of critical AMS readiness categories (REQ-004, REQ-007)
CREATE TABLE readiness_question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL UNIQUE,
    question_text TEXT NOT NULL,
    is_critical INTEGER NOT NULL DEFAULT 1 CHECK (is_critical IN (0, 1))
);

-- Assessment: one readiness assessment per transition scope (REQ-002, REQ-003)
CREATE TABLE assessment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    submitted_by TEXT,
    submitted_at TEXT,
    FOREIGN KEY (submitted_by) REFERENCES user_role(username)
);

-- Evidence: proof linked to a readiness category, with source/owner/freshness (REQ-004, REQ-006)
CREATE TABLE evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    source TEXT NOT NULL,
    owner TEXT NOT NULL,
    freshness_date TEXT NOT NULL,   -- ISO date YYYY-MM-DD
    criticality TEXT NOT NULL CHECK (criticality IN ('Critical', 'Important', 'Optional')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (assessment_id) REFERENCES assessment(id),
    FOREIGN KEY (category) REFERENCES readiness_question(category)
);

-- RFC: structured request-for-comment raised by a Transition Lead to a Contributor,
-- capturing documented transition knowledge (REQ-012, REQ-013)
-- Added by change request "RFC tool" - see docs/09_change_request.md
CREATE TABLE rfc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    category TEXT,                         -- optional link to a readiness category
    title TEXT NOT NULL,
    question TEXT NOT NULL,
    raised_by TEXT NOT NULL,               -- must be TransitionLead (enforced in rfc_rules.py)
    assigned_to TEXT,                      -- expected Contributor, optional
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'answered')),
    answer_text TEXT,
    answered_by TEXT,
    is_faq_candidate INTEGER NOT NULL DEFAULT 0 CHECK (is_faq_candidate IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    answered_at TEXT,
    FOREIGN KEY (assessment_id) REFERENCES assessment(id),
    FOREIGN KEY (category) REFERENCES readiness_question(category),
    FOREIGN KEY (raised_by) REFERENCES user_role(username),
    FOREIGN KEY (assigned_to) REFERENCES user_role(username),
    FOREIGN KEY (answered_by) REFERENCES user_role(username)
);
