Feature: Repository CLI operations

  Scenario: Updating fixes validation
    Given I initialize a repository
    And I create the source file "source.py"
    And I create an anchor for "source.py" at offset 3
    When I modify "source.py"
    And I update the repository
    Then the repository is valid
