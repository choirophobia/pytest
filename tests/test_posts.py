import pytest

from services.posts_api import posts_api

NOT_FOUND_STATUSES = (404, 429)


class TestRead:
    def test_lists_posts_with_default_pagination(self):
        response = posts_api.list()

        assert response.status_code == 200
        body = response.json()
        assert "posts" in body
        assert body["total"] > 0

    def test_gets_a_single_post_by_id(self):
        response = posts_api.get_by_id(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert "title" in body
        assert "body" in body

    def test_searches_posts_by_query(self):
        response = posts_api.search("love")

        assert response.status_code == 200
        body = response.json()
        assert "posts" in body
        assert body["total"] >= 0

    def test_gets_posts_for_a_user(self):
        response = posts_api.get_by_user(1)

        assert response.status_code == 200
        body = response.json()
        assert "posts" in body
        for post in body["posts"]:
            assert post["userId"] == 1


class TestCreate:
    def test_creates_a_new_post(self):
        payload = {"title": "Test Post", "body": "This is a test post body", "userId": 1}

        response = posts_api.create(payload)

        assert response.status_code == 201
        body = response.json()
        assert body["title"] == payload["title"]
        assert body["body"] == payload["body"]
        assert body["userId"] == payload["userId"]
        assert "id" in body


class TestUpdate:
    def test_updates_a_post_with_put(self):
        payload = {"title": "Updated Title"}

        response = posts_api.update(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["title"] == payload["title"]

    def test_partially_updates_a_post_with_patch(self):
        payload = {"title": "Patched Title"}

        response = posts_api.patch(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["title"] == payload["title"]


class TestDelete:
    def test_deletes_a_post(self):
        response = posts_api.remove(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["isDeleted"] is True
        assert "deletedOn" in body


@pytest.mark.negative
class TestNegativeCases:
    def test_get_by_id_with_out_of_range_id_returns_not_found(self):
        response = posts_api.get_by_id(999999)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_update_with_out_of_range_id_returns_not_found(self):
        response = posts_api.update(999999, {"title": "Does not matter"})

        assert response.status_code in NOT_FOUND_STATUSES

    def test_delete_with_out_of_range_id_returns_not_found(self):
        response = posts_api.remove(999999)

        assert response.status_code in NOT_FOUND_STATUSES
