Feature: Adding an anchor from the CLI

  Scenario: Create a new anchor
    Given I initialize a repository
    And I create the source file "source.py"
    When I create an anchor for "source.py" at offset 3
    Then an anchor for "source.py" at offset 3 appears in the listing
    And the repository has 1 anchor

  Scenario: Creating two anchors for the same file
    Given I initialize a repository
    And I create the source file "source.py"
    When I create an anchor for "source.py" at offset 3
    And I create an anchor for "source.py" at offset 2
    Then an anchor for "source.py" at offset 3 appears in the listing
    And an anchor for "source.py" at offset 2 appears in the listing
    And the repository has 2 anchor

  Scenario: Can not create anchor for missing file
    Given I initialize a repository
    Then I can not create an anchor for "source.py"
