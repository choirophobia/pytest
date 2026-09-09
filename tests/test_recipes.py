import pytest

from services.recipes_api import recipes_api

NOT_FOUND_STATUSES = (404, 429)


class TestRead:
    def test_lists_recipes_with_default_pagination(self):
        response = recipes_api.list()

        assert response.status_code == 200
        body = response.json()
        assert "recipes" in body
        assert body["total"] > 0

    def test_gets_a_single_recipe_by_id(self):
        response = recipes_api.get_by_id(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert "name" in body
        assert "ingredients" in body
        assert "instructions" in body

    def test_searches_recipes_by_query(self):
        response = recipes_api.search("pizza")

        assert response.status_code == 200
        body = response.json()
        assert "recipes" in body
        assert body["total"] >= 0

    def test_gets_recipes_by_tag(self):
        response = recipes_api.get_by_tag("Pizza")

        assert response.status_code == 200
        body = response.json()
        assert "recipes" in body
        for recipe in body["recipes"]:
            assert "Pizza" in recipe["tags"]


class TestCreate:
    def test_creates_a_new_recipe(self):
        payload = {
            "name": "Test Recipe",
            "ingredients": ["Test ingredient"],
            "instructions": ["Test instruction"],
        }

        response = recipes_api.create(payload)

        assert response.status_code == 201
        body = response.json()
        assert body["name"] == payload["name"]
        assert body["ingredients"] == payload["ingredients"]
        assert "id" in body


class TestUpdate:
    def test_updates_a_recipe_with_put(self):
        payload = {"name": "Updated Recipe Name"}

        response = recipes_api.update(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["name"] == payload["name"]

    def test_partially_updates_a_recipe_with_patch(self):
        payload = {"name": "Patched Recipe Name"}

        response = recipes_api.patch(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["name"] == payload["name"]


class TestDelete:
    def test_deletes_a_recipe(self):
        response = recipes_api.remove(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["isDeleted"] is True
        assert "deletedOn" in body


@pytest.mark.negative
class TestNegativeCases:
    def test_get_by_id_with_out_of_range_id_returns_not_found(self):
        response = recipes_api.get_by_id(999999)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_update_with_out_of_range_id_returns_not_found(self):
        response = recipes_api.update(999999, {"name": "Does not matter"})

        assert response.status_code in NOT_FOUND_STATUSES

    def test_delete_with_out_of_range_id_returns_not_found(self):
        response = recipes_api.remove(999999)

        assert response.status_code in NOT_FOUND_STATUSES
