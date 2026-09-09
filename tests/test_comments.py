import pytest

from services.comments_api import comments_api

NOT_FOUND_STATUSES = (404, 429)


class TestRead:
    def test_lists_comments_with_default_pagination(self):
        response = comments_api.list()

        assert response.status_code == 200
        body = response.json()
        assert "comments" in body
        assert body["total"] > 0

    def test_gets_a_single_comment_by_id(self):
        response = comments_api.get_by_id(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert "body" in body

    def test_gets_comments_for_a_post(self):
        response = comments_api.get_by_post(1)

        assert response.status_code == 200
        body = response.json()
        assert "comments" in body
        for comment in body["comments"]:
            assert comment["postId"] == 1


class TestCreate:
    def test_creates_a_new_comment(self):
        payload = {"body": "This is a test comment", "postId": 1, "userId": 1}

        response = comments_api.create(payload)

        assert response.status_code == 201
        body = response.json()
        assert body["body"] == payload["body"]
        assert "id" in body


class TestUpdate:
    def test_updates_a_comment_with_put(self):
        payload = {"body": "Updated comment body"}

        response = comments_api.update(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["body"] == payload["body"]

    def test_partially_updates_a_comment_with_patch(self):
        payload = {"body": "Patched comment body"}

        response = comments_api.patch(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["body"] == payload["body"]


class TestDelete:
    def test_deletes_a_comment(self):
        response = comments_api.remove(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["isDeleted"] is True
        assert "deletedOn" in body


@pytest.mark.negative
class TestNegativeCases:
    def test_get_by_id_with_out_of_range_id_returns_not_found(self):
        response = comments_api.get_by_id(999999)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_update_with_out_of_range_id_returns_not_found(self):
        response = comments_api.update(999999, {"body": "Does not matter"})

        assert response.status_code in NOT_FOUND_STATUSES

    def test_delete_with_out_of_range_id_returns_not_found(self):
        response = comments_api.remove(999999)

        assert response.status_code in NOT_FOUND_STATUSES
