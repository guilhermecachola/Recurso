-- Seed data for AMS Transition Intake & Readiness Assessment
-- Provides valid AND invalid cases, used both by the app demo and by automated tests
-- (tests/test_readiness_database.py loads an equivalent independent seed for isolation)

-- Users / roles (REQ-008)
INSERT INTO user_role (username, role) VALUES ('alice.lead', 'TransitionLead');
INSERT INTO user_role (username, role) VALUES ('bruno.contrib', 'Contributor');
INSERT INTO user_role (username, role) VALUES ('carla.manager', 'AMSManager');
INSERT INTO user_role (username, role) VALUES ('diana.security', 'SecurityOfficer');

-- Critical readiness categories (REQ-004, REQ-007)
INSERT INTO readiness_question (category, question_text, is_critical) VALUES
    ('Monitoring', 'Are monitoring dashboards and alert ownership documented?', 1);
INSERT INTO readiness_question (category, question_text, is_critical) VALUES
    ('DR', 'Is the Disaster Recovery procedure documented with recent test evidence?', 1);
INSERT INTO readiness_question (category, question_text, is_critical) VALUES
    ('Access', 'Is the access/permissions procedure documented?', 1);
INSERT INTO readiness_question (category, question_text, is_critical) VALUES
    ('Integrations', 'Are integrations and dependencies documented?', 1);
INSERT INTO readiness_question (category, question_text, is_critical) VALUES
    ('SLA', 'Is current SLA information available and confirmed?', 1);

-- Assessment 1: OrderCare — will be COMPLETE with fresh evidence (happy path demo)
INSERT INTO assessment (id, name, status, created_at) VALUES
    (1, 'OrderCare - EU Region Transition', 'draft', '2026-07-01 09:00:00');

-- Assessment 2: OrderCare — INCOMPLETE, missing DR evidence (negative demo)
INSERT INTO assessment (id, name, status, created_at) VALUES
    (2, 'OrderCare - LATAM Region Transition', 'draft', '2026-07-05 09:00:00');

-- Evidence for Assessment 1 (complete set, evidence within 90 days -> not stale)
INSERT INTO evidence (assessment_id, category, source, owner, freshness_date, criticality) VALUES
    (1, 'Monitoring', 'Datadog export', 'carla.manager', '2026-06-20', 'Critical');
INSERT INTO evidence (assessment_id, category, source, owner, freshness_date, criticality) VALUES
    (1, 'DR', 'DR test report Q2', 'diana.security', '2026-05-15', 'Critical');
INSERT INTO evidence (assessment_id, category, source, owner, freshness_date, criticality) VALUES
    (1, 'Access', 'IAM access matrix', 'diana.security', '2026-06-01', 'Critical');
INSERT INTO evidence (assessment_id, category, source, owner, freshness_date, criticality) VALUES
    (1, 'Integrations', 'Integration inventory sheet', 'bruno.contrib', '2026-06-25', 'Important');
INSERT INTO evidence (assessment_id, category, source, owner, freshness_date, criticality) VALUES
    (1, 'SLA', 'Signed SLA document', 'carla.manager', '2026-06-10', 'Critical');

-- Evidence for Assessment 2 (missing DR category entirely; also one stale item)
INSERT INTO evidence (assessment_id, category, source, owner, freshness_date, criticality) VALUES
    (2, 'Monitoring', 'Grafana screenshot', 'bruno.contrib', '2026-03-01', 'Critical'); -- >90 days old -> stale
INSERT INTO evidence (assessment_id, category, source, owner, freshness_date, criticality) VALUES
    (2, 'Access', 'Access list (old export)', 'bruno.contrib', '2026-06-01', 'Critical');
INSERT INTO evidence (assessment_id, category, source, owner, freshness_date, criticality) VALUES
    (2, 'SLA', 'SLA email confirmation', 'carla.manager', '2026-06-15', 'Important');
-- Note: no 'DR' and no 'Integrations' evidence for assessment 2 -> critical gaps

-- RFCs (added by change request "RFC tool" - see docs/09_change_request.md)
-- RFC 1: open, raised by TransitionLead against assessment 2's missing DR evidence
INSERT INTO rfc (id, assessment_id, category, title, question, raised_by, assigned_to, status, created_at) VALUES
    (1, 2, 'DR', 'Missing DR evidence for LATAM transition',
     'We have no DR test report for the LATAM OrderCare deployment. Can you confirm whether a DR test was ever run, and share the report or a contact who has it?',
     'alice.lead', 'bruno.contrib', 'open', '2026-07-06 10:00:00');

-- RFC 2: answered, already resolved and marked as an FAQ candidate for future AMS transitions
INSERT INTO rfc (id, assessment_id, category, title, question, raised_by, assigned_to, status,
                  answer_text, answered_by, is_faq_candidate, created_at, answered_at) VALUES
    (2, 1, 'Integrations', 'Which systems does OrderCare integrate with?',
     'The integration inventory sheet lists 4 systems but does not say which are still active. Can you confirm the current active integration list?',
     'alice.lead', 'bruno.contrib', 'answered',
     'OrderCare currently integrates with: Payment Gateway (active), Warehouse Management System (active), legacy Loyalty Points service (deprecated, read-only), and the old EDI B2B connector (decommissioned, safe to ignore).',
     'bruno.contrib', 1, '2026-06-28 09:00:00', '2026-06-29 14:30:00');

-- RFC 3: open, no assigned Contributor yet (unassigned request), used to test the "assigned_to optional" case
INSERT INTO rfc (id, assessment_id, category, title, question, raised_by, assigned_to, status, created_at) VALUES
    (3, 1, 'SLA', 'Confirm SLA penalty clauses',
     'The signed SLA document does not mention penalty clauses for downtime. Does a separate penalty annex exist?',
     'alice.lead', NULL, 'open', '2026-07-10 11:00:00');
