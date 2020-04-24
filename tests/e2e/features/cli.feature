Feature: Command line interface

  Scenario: Initialize repository
    Given I initialize a repository
    Then a repo data directory exists

  Scenario: Create a new anchor
    Given I initialize a repository
    And I create the source file "source.py"
    When I create a new anchor for "source.py" at offset 19
    Then an anchor for "source.py" at line 3 appears in the listing

  Scenario: Validate unchanged source
    Given I initialize a repository
    And I create the source file "source.py"
    When I create a new anchor for "source.py" at offset 19
    Then the repository is valid

  Scenario: Validate modified source
    Given I initialize a repository
    And I create the source file "source.py"
    When I create a new anchor for "source.py" at offset 19
    When I modify "source.py"
    Then the repository is invalid

  Scenario: External files are rejected
    Given I initialize a repository
    Then anchoring an external file fails
