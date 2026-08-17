"""Response-shape checks via JSON Schema, layered on top of the field-by-field
assertions in test_products.py/test_users.py/test_carts.py. Where those assert
specific values (id == 1, price > 0), these assert the response's overall
*shape* against schemas/*.json - see the README's JSON Schema section for why
this is worth having as a separate, dedicated layer.
"""
from schemas.validator import assert_matches_schema
from services.carts_api import carts_api
from services.products_api import products_api
from services.users_api import users_api


def test_product_matches_schema():
    response = products_api.get_by_id(1)

    assert response.status_code == 200
    assert_matches_schema(response.json(), "product")


def test_user_matches_schema():
    response = users_api.get_by_id(1)

    assert response.status_code == 200
    assert_matches_schema(response.json(), "user")


def test_cart_matches_schema():
    response = carts_api.get_by_id(1)

    assert response.status_code == 200
    assert_matches_schema(response.json(), "cart")
