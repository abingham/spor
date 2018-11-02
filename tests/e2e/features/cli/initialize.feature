Feature: Initializing a repository

  Scenario: Initialize repository
    Given I initialize a repository
    Then a repo data directory exists

  Scenario: Repository already exists
    Given I initialize a repository
    Then reinitializing fails
