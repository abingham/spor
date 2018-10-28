Feature: Adding an anchor from the CLI

  Scenario: Create a new anchor
    Given I initialize a repository
    And I create the source file "source.py"
    When I create a new anchor for "source.py" at offset 3
    Then an anchor for "source.py" at offset 3 appears in the listing
