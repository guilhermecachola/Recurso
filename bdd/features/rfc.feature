Feature: RFC (Request for Comment) tool
  Added by change request (see docs/09_change_request.md).
  The goal is to let a Transition Lead formally request missing transition information
  from a Contributor, and to persist the answer as structured, reusable documentation.
  Related requirements: REQ-012, REQ-013

  Scenario: Happy path — Transition Lead raises an RFC and Contributor answers it
    Given a Transition Lead has opened a readiness assessment
    When the Transition Lead raises an RFC with a title and a question assigned to a Contributor
    Then the RFC is created with status "open"
    When the Contributor submits a non-empty answer to that RFC
    Then the RFC status becomes "answered"
    And the answer is recorded with the Contributor's username

  Scenario: Missing required fields — RFC cannot be raised without a title and question
    Given a Transition Lead has opened a readiness assessment
    When the Transition Lead tries to raise an RFC without a question
    Then the RFC is not created
    And the system reports missing required fields

  Scenario: Unauthorized user — Contributor cannot raise an RFC
    Given a Contributor has opened a readiness assessment
    When the Contributor tries to raise an RFC
    Then the RFC is not created
    And the system reports an unauthorized role

  Scenario: Unauthorized user — Security Officer cannot answer an RFC
    Given an open RFC exists on a readiness assessment
    When a Security Officer tries to answer the RFC
    Then the answer is not saved
    And the RFC remains in "open" status
