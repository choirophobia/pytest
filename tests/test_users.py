import re

import pytest

from services.users_api import users_api

NOT_FOUND_STATUSES = (404, 429)
BAD_REQUEST_STATUSES = (400, 429)


class TestRead:
    def test_lists_users_with_default_pagination(self):
        response = users_api.list()

        assert response.status_code == 200
        body = response.json()
        assert "users" in body
        assert body["limit"] == 30
        assert body["skip"] == 0
        assert body["total"] > 0
        assert len(body["users"]) == 30
        for user in body["users"]:
            assert isinstance(user["id"], int)
            assert isinstance(user["firstName"], str) and user["firstName"]
            assert isinstance(user["email"], str) and "@" in user["email"]

    def test_lists_users_with_limit_and_skip(self):
        response = users_api.list(limit=5, skip=10)

        assert response.status_code == 200
        body = response.json()
        assert len(body["users"]) == 5
        assert body["skip"] == 10

    def test_gets_a_single_user_by_id(self):
        response = users_api.get_by_id(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert isinstance(body["firstName"], str) and body["firstName"]
        assert isinstance(body["email"], str) and "@" in body["email"]
        assert isinstance(body["age"], int) and body["age"] > 0
        assert body["gender"] in ("male", "female")
        assert isinstance(body["username"], str) and body["username"]
        assert "city" in body["address"]
        assert "country" in body["address"]

    def test_searches_users_by_query(self):
        response = users_api.search("Emily")

        assert response.status_code == 200
        body = response.json()
        assert "users" in body
        # "Emily" matches fewer users than the default page size (30), so
        # every match is returned in one page - total and returned count agree.
        assert body["total"] == len(body["users"])
        for user in body["users"]:
            haystack = f"{user['firstName']} {user['lastName']} {user['email']}".lower()
            assert "emily" in haystack

    def test_filters_users_by_key_and_value(self):
        response = users_api.filter("hair.color", "Brown")

        assert response.status_code == 200
        body = response.json()
        assert "users" in body
        # this filter matches fewer users than the default page size, so the
        # whole match set is returned in one page.
        assert body["total"] == len(body["users"])
        for user in body["users"]:
            assert user["hair"]["color"] == "Brown"

    def test_lists_users_sorted_ascending_by_age(self):
        response = users_api.list(sortBy="age", order="asc", limit=10)

        assert response.status_code == 200
        ages = [user["age"] for user in response.json()["users"]]
        assert ages == sorted(ages)

    def test_search_with_no_matches_returns_empty_list(self):
        response = users_api.search("zzzznomatchxyz")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 0
        assert body["users"] == []

    def test_filter_with_unknown_key_returns_empty_list_not_an_error(self):
        response = users_api.filter("notarealkey", "x")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 0
        assert body["users"] == []


class TestCreate:
    def test_creates_a_new_user(self):
        payload = {"firstName": "Test", "lastName": "User", "age": 25}

        response = users_api.create(payload)

        assert response.status_code == 201
        body = response.json()
        assert body["firstName"] == payload["firstName"]
        assert body["lastName"] == payload["lastName"]
        assert body["age"] == payload["age"]
        assert isinstance(body["id"], int)


class TestUpdate:
    def test_updates_a_user_with_put(self):
        payload = {"firstName": "UpdatedName"}

        response = users_api.update(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["firstName"] == payload["firstName"]
        # DummyJSON's PUT merges rather than fully replacing the resource -
        # fields outside the payload survive in the echoed response.
        assert "lastName" in body
        assert "email" in body

    def test_partially_updates_a_user_with_patch(self):
        payload = {"age": 40}

        response = users_api.patch(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["age"] == payload["age"]
        assert "firstName" in body
        assert "email" in body


class TestDelete:
    def test_deletes_a_user(self):
        response = users_api.remove(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["isDeleted"] is True
        # e.g. "2026-08-09T14:40:23.561Z"
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$", body["deletedOn"])
        # the full user is echoed back, not just an id/flag pair
        assert isinstance(body["firstName"], str) and body["firstName"]
        assert "email" in body


@pytest.mark.negative
class TestNegativeCases:
    def test_get_by_id_with_out_of_range_id_returns_not_found(self):
        response = users_api.get_by_id(999999)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_update_with_out_of_range_id_returns_not_found(self):
        response = users_api.update(999999, {"firstName": "Does not matter"})

        assert response.status_code in NOT_FOUND_STATUSES

    def test_delete_with_out_of_range_id_returns_not_found(self):
        response = users_api.remove(999999)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_get_by_id_zero_returns_not_found(self):
        response = users_api.get_by_id(0)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_get_by_id_negative_returns_not_found(self):
        response = users_api.get_by_id(-1)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_get_by_id_with_non_numeric_id_returns_bad_request(self):
        # Unlike /products/{id}, which 404s on a non-numeric id, /users/{id}
        # rejects it outright with a 400 - the two resources validate the
        # path param differently.
        response = users_api.get_by_id("not-a-valid-id")

        assert response.status_code in BAD_REQUEST_STATUSES

    def test_update_with_non_numeric_id_returns_bad_request(self):
        response = users_api.update("not-a-valid-id", {"firstName": "Does not matter"})

        assert response.status_code in BAD_REQUEST_STATUSES

    def test_delete_with_non_numeric_id_returns_bad_request(self):
        response = users_api.remove("not-a-valid-id")

        assert response.status_code in BAD_REQUEST_STATUSES
