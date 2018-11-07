Feature: Initializing a repository

  Scenario: Initialize repository
    Given I initialize a repository
    Then a repo data directory exists

  Scenario: Repository already exists
    Given I initialize a repository
    Then reinitializing the repository fails

  Scenario: Repository is initially empty
    Given I initialize a repository
    Then the repository has 0 anchors
