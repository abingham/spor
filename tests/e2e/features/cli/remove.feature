Feature: Removing an anchor from the CLI

  Scenario: Remove an existing anchor
    Given I initialize a repository
    And I create the source file "source.py"
    And I create an anchor for "source.py" at offset 3
    When I delete the anchor for "source.py" at offset 3
    Then no anchor for "source.py" at offset 3 appears in the listing
