Feature: AMS readiness assessment
  The goal is to validate that transition readiness information is collected with evidence and role control.
  Related requirements: REQ-003, REQ-004, REQ-005, REQ-009

  Scenario: Happy path — Transition Lead submits complete readiness assessment
    Given a Transition Lead has created a readiness assessment
    And all critical evidence categories are complete
    When the Transition Lead submits the assessment
    Then the assessment is marked as submitted
    And no critical missing information is shown

  Scenario: Missing evidence — submission is blocked
    Given a Transition Lead has created a readiness assessment
    And the DR evidence category is missing
    When the Transition Lead tries to submit the assessment
    Then the submission is blocked
    And the system displays the missing critical information

  Scenario: Unauthorized user — Contributor cannot submit final assessment
    Given a Contributor has edited draft evidence
    When the Contributor tries to submit the final assessment
    Then the submission is denied
    And the assessment remains in draft status

  Scenario: Stale evidence is flagged but does not block submission
    Given a Transition Lead has created a readiness assessment
    And all critical evidence categories are complete
    But one evidence item is older than 90 days
    When the Transition Lead submits the assessment
    Then the assessment is marked as submitted
    And the stale evidence item is flagged as stale
