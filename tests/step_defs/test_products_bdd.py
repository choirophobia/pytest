"""pytest-bdd prototype: same products_api service object as test_products.py,
driven by Gherkin scenarios instead of plain pytest functions. See
features/products.feature and the README's Cucumber/BDD comparison section.
"""
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from services.products_api import products_api

scenarios("../../features/products.feature")

NOT_FOUND_STATUSES = (404, 429)


@given(parsers.parse("a product with id {product_id:d}"), target_fixture="context")
def a_product_with_id(product_id):
    return {"product_id": product_id}


@given(
    parsers.parse('a new product payload with title "{title}" and price {price:f}'),
    target_fixture="context",
)
def a_new_product_payload(title, price):
    return {"payload": {"title": title, "price": price, "category": "test-category"}}


@when("I request the product by id")
def request_product_by_id(context):
    context["response"] = products_api.get_by_id(context["product_id"])


@when("I create the product")
def create_the_product(context):
    context["response"] = products_api.create(context["payload"])


@then(parsers.parse("the response status code is {status:d}"))
def response_status_code_is(context, status):
    assert context["response"].status_code == status


@then("the response status code indicates not found")
def response_status_code_indicates_not_found(context):
    assert context["response"].status_code in NOT_FOUND_STATUSES


@then("the product's title and price are present")
def title_and_price_are_present(context):
    body = context["response"].json()
    assert "title" in body
    assert "price" in body


@then("the created product echoes the payload")
def created_product_echoes_the_payload(context):
    body = context["response"].json()
    assert body["title"] == context["payload"]["title"]
    assert body["price"] == context["payload"]["price"]
