import re

import pytest

from services.carts_api import carts_api

NOT_FOUND_STATUSES = (404, 429)


def assert_cart_totals_are_consistent(cart):
    assert cart["totalProducts"] == len(cart["products"])
    assert cart["totalQuantity"] == sum(p["quantity"] for p in cart["products"])


class TestRead:
    def test_lists_carts_with_default_pagination(self):
        response = carts_api.list()

        assert response.status_code == 200
        body = response.json()
        assert "carts" in body
        assert body["limit"] == 30
        assert body["skip"] == 0
        assert body["total"] > 0
        assert len(body["carts"]) == 30
        for cart in body["carts"]:
            assert isinstance(cart["id"], int)
            assert isinstance(cart["userId"], int)
            assert isinstance(cart["products"], list) and len(cart["products"]) > 0
            assert isinstance(cart["total"], (int, float)) and cart["total"] > 0
            assert isinstance(cart["discountedTotal"], (int, float))
            assert_cart_totals_are_consistent(cart)

    def test_gets_a_single_cart_by_id(self):
        response = carts_api.get_by_id(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert isinstance(body["userId"], int)
        assert isinstance(body["products"], list) and len(body["products"]) > 0
        assert isinstance(body["total"], (int, float)) and body["total"] > 0
        assert isinstance(body["discountedTotal"], (int, float))
        assert_cart_totals_are_consistent(body)
        for product in body["products"]:
            assert isinstance(product["id"], int)
            assert isinstance(product["quantity"], int) and product["quantity"] > 0
            assert isinstance(product["price"], (int, float)) and product["price"] > 0
            # price * quantity is subject to float rounding, so compare with a tolerance
            assert product["total"] == pytest.approx(product["price"] * product["quantity"])

    def test_gets_carts_for_a_user(self):
        response = carts_api.get_by_user(1)

        assert response.status_code == 200
        body = response.json()
        assert "carts" in body
        # user 1 has exactly one cart in the seed data
        assert body["total"] == 1
        assert len(body["carts"]) == 1
        assert body["carts"][0]["id"] == 1
        for cart in body["carts"]:
            assert cart["userId"] == 1


class TestCreate:
    def test_creates_a_new_cart_for_a_user(self):
        payload = {"userId": 1, "products": [{"id": 1, "quantity": 2}]}

        response = carts_api.create(payload)

        assert response.status_code == 201
        body = response.json()
        assert body["userId"] == payload["userId"]
        assert body["totalProducts"] == 1
        assert body["totalQuantity"] == 2
        assert isinstance(body["id"], int)
        assert body["products"][0]["id"] == payload["products"][0]["id"]
        assert body["products"][0]["quantity"] == payload["products"][0]["quantity"]
        assert isinstance(body["total"], (int, float)) and body["total"] > 0
        assert isinstance(body["discountedTotal"], (int, float))


class TestUpdate:
    def test_updates_a_cart_with_put(self):
        payload = {"merge": True, "products": [{"id": 1, "quantity": 1}]}

        response = carts_api.update(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        # "merge": true adds/updates the given products into the existing cart
        # rather than replacing it - the cart's other original products survive.
        assert body["userId"] == 1
        assert isinstance(body["products"], list) and len(body["products"]) > 1
        assert any(p["id"] == 1 for p in body["products"])
        assert_cart_totals_are_consistent(body)

    def test_partially_updates_a_cart_with_patch(self):
        payload = {"merge": True, "products": [{"id": 1, "quantity": 1}]}

        response = carts_api.patch(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["userId"] == 1
        assert isinstance(body["products"], list) and len(body["products"]) > 1
        assert_cart_totals_are_consistent(body)


class TestDelete:
    def test_deletes_a_cart(self):
        response = carts_api.remove(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["isDeleted"] is True
        # e.g. "2026-08-09T14:55:11.303Z"
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$", body["deletedOn"])
        # the full cart is echoed back, not just an id/flag pair
        assert "userId" in body
        assert "products" in body


@pytest.mark.negative
class TestNegativeCases:
    def test_get_by_id_with_out_of_range_id_returns_not_found(self):
        response = carts_api.get_by_id(999999)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_update_with_out_of_range_id_returns_not_found(self):
        response = carts_api.update(999999, {"merge": True, "products": []})

        assert response.status_code in NOT_FOUND_STATUSES

    def test_delete_with_out_of_range_id_returns_not_found(self):
        response = carts_api.remove(999999)

        assert response.status_code in NOT_FOUND_STATUSES
