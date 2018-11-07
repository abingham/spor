Feature: Repository CLI operations

  Background:
    Given I initialize a repository
    And I create the source file "source.py"

  Scenario: Validate unchanged source
    When I create an anchor for "source.py" at offset 3
    Then the repository is valid

  Scenario: Validate modified source
    When I create an anchor for "source.py" at offset 3
    When I modify "source.py"
    Then the repository is invalid
