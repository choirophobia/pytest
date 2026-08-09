import re

import pytest

from services.products_api import products_api

NOT_FOUND_STATUSES = (404, 429)


class TestRead:
    def test_lists_products_with_default_pagination(self):
        response = products_api.list()

        assert response.status_code == 200
        body = response.json()
        assert "products" in body
        assert body["limit"] == 30
        assert body["skip"] == 0
        assert body["total"] > 0
        assert len(body["products"]) == 30
        for product in body["products"]:
            assert isinstance(product["id"], int)
            assert isinstance(product["title"], str) and product["title"]
            assert isinstance(product["price"], (int, float)) and product["price"] > 0
            assert isinstance(product["category"], str) and product["category"]

    def test_lists_products_with_limit_and_skip(self):
        response = products_api.list(limit=5, skip=10)

        assert response.status_code == 200
        body = response.json()
        assert len(body["products"]) == 5
        assert body["skip"] == 10

    def test_gets_a_single_product_by_id(self):
        response = products_api.get_by_id(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert isinstance(body["title"], str) and body["title"]
        assert isinstance(body["price"], (int, float)) and body["price"] > 0
        assert isinstance(body["description"], str) and body["description"]
        assert isinstance(body["category"], str) and body["category"]
        assert isinstance(body["stock"], int) and body["stock"] >= 0
        assert isinstance(body["rating"], (int, float))

    def test_searches_products_by_query(self):
        response = products_api.search("phone")

        assert response.status_code == 200
        body = response.json()
        assert "products" in body
        assert body["total"] >= 0
        # "phone" matches fewer products than the default page size (30), so
        # every match is returned in one page - total and returned count agree.
        assert body["total"] == len(body["products"])
        for product in body["products"]:
            haystack = f"{product['title']} {product['description']}".lower()
            assert "phone" in haystack

    def test_lists_products_sorted_ascending_by_price(self):
        response = products_api.list(sortBy="price", order="asc", limit=10)

        assert response.status_code == 200
        prices = [product["price"] for product in response.json()["products"]]
        assert prices == sorted(prices)

    def test_lists_products_sorted_descending_by_title(self):
        response = products_api.list(sortBy="title", order="desc", limit=10)

        assert response.status_code == 200
        titles = [product["title"] for product in response.json()["products"]]
        assert titles == sorted(titles, reverse=True)

    def test_lists_product_categories(self):
        response = products_api.get_categories()

        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) > 0
        for category in body:
            assert set(category.keys()) == {"slug", "name", "url"}
            assert category["url"] == f"https://dummyjson.com/products/category/{category['slug']}"

    def test_gets_products_by_category(self):
        response = products_api.get_by_category("smartphones")

        assert response.status_code == 200
        body = response.json()
        assert "products" in body
        # smartphones has fewer products than the default page size, so this
        # category page returns everything in one shot.
        assert body["total"] == len(body["products"])
        for product in body["products"]:
            assert product["category"] == "smartphones"


class TestCreate:
    def test_creates_a_new_product(self):
        payload = {"title": "Test Product", "price": 19.99, "category": "test-category"}

        response = products_api.create(payload)

        assert response.status_code == 201
        body = response.json()
        assert body["title"] == payload["title"]
        assert body["price"] == payload["price"]
        assert body["category"] == payload["category"]
        assert isinstance(body["id"], int)


class TestUpdate:
    def test_updates_a_product_with_put(self):
        payload = {"title": "Updated Product Title"}

        response = products_api.update(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["title"] == payload["title"]
        # DummyJSON's PUT merges rather than fully replacing the resource -
        # fields outside the payload survive in the echoed response.
        assert "price" in body
        assert "category" in body

    def test_partially_updates_a_product_with_patch(self):
        payload = {"price": 999.99}

        response = products_api.patch(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["price"] == payload["price"]
        assert "title" in body
        assert "category" in body


class TestDelete:
    def test_deletes_a_product(self):
        response = products_api.remove(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["isDeleted"] is True
        # e.g. "2026-08-09T14:40:23.561Z"
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$", body["deletedOn"])
        # the full product is echoed back, not just an id/flag pair
        assert isinstance(body["title"], str) and body["title"]
        assert "price" in body


@pytest.mark.negative
class TestNegativeCases:
    def test_get_by_id_with_out_of_range_id_returns_not_found(self):
        response = products_api.get_by_id(999999)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_update_with_out_of_range_id_returns_not_found(self):
        response = products_api.update(999999, {"title": "Does not matter"})

        assert response.status_code in NOT_FOUND_STATUSES

    def test_delete_with_out_of_range_id_returns_not_found(self):
        response = products_api.remove(999999)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_get_by_id_with_non_numeric_id_returns_not_found(self):
        response = products_api.get_by_id("not-a-valid-id")

        assert response.status_code in NOT_FOUND_STATUSES
