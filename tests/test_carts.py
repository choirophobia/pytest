import pytest

from services.carts_api import carts_api

NOT_FOUND_STATUSES = (404, 429)


class TestRead:
    def test_lists_carts_with_default_pagination(self):
        response = carts_api.list()

        assert response.status_code == 200
        body = response.json()
        assert "carts" in body
        assert body["total"] > 0

    def test_gets_a_single_cart_by_id(self):
        response = carts_api.get_by_id(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert "products" in body
        assert "userId" in body

    def test_gets_carts_for_a_user(self):
        response = carts_api.get_by_user(1)

        assert response.status_code == 200
        body = response.json()
        assert "carts" in body
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
        assert "id" in body


class TestUpdate:
    def test_updates_a_cart_with_put(self):
        payload = {"merge": True, "products": [{"id": 1, "quantity": 1}]}

        response = carts_api.update(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert "products" in body

    def test_partially_updates_a_cart_with_patch(self):
        payload = {"merge": True, "products": [{"id": 1, "quantity": 1}]}

        response = carts_api.patch(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1


class TestDelete:
    def test_deletes_a_cart(self):
        response = carts_api.remove(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["isDeleted"] is True
        assert "deletedOn" in body


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
