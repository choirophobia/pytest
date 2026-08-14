Feature: Product management
  As a QA engineer testing the DummyJSON API
  I want to verify product CRUD operations
  So that I can be confident products behave as expected

  Scenario: Fetching a single product by id
    Given a product with id 1
    When I request the product by id
    Then the response status code is 200
    And the product's title and price are present

  Scenario: Creating a new product
    Given a new product payload with title "Test Product" and price 19.99
    When I create the product
    Then the response status code is 201
    And the created product echoes the payload

  Scenario: Fetching a product that does not exist
    Given a product with id 999999
    When I request the product by id
    Then the response status code indicates not found
