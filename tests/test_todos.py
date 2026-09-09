import pytest

from services.todos_api import todos_api

NOT_FOUND_STATUSES = (404, 429)


class TestRead:
    def test_lists_todos_with_default_pagination(self):
        response = todos_api.list()

        assert response.status_code == 200
        body = response.json()
        assert "todos" in body
        assert body["total"] > 0

    def test_gets_a_single_todo_by_id(self):
        response = todos_api.get_by_id(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert "todo" in body
        assert "completed" in body

    def test_gets_a_random_todo(self):
        response = todos_api.get_random()

        assert response.status_code == 200
        body = response.json()
        assert "id" in body
        assert "todo" in body

    def test_gets_todos_for_a_user(self):
        response = todos_api.get_by_user(1)

        assert response.status_code == 200
        body = response.json()
        assert "todos" in body
        for todo in body["todos"]:
            assert todo["userId"] == 1


class TestCreate:
    def test_creates_a_new_todo(self):
        payload = {"todo": "Write more tests", "completed": False, "userId": 1}

        response = todos_api.create(payload)

        assert response.status_code == 201
        body = response.json()
        assert body["todo"] == payload["todo"]
        assert body["completed"] == payload["completed"]
        assert body["userId"] == payload["userId"]
        assert "id" in body


class TestUpdate:
    def test_updates_a_todo_with_put(self):
        payload = {"completed": True}

        response = todos_api.update(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["completed"] == payload["completed"]

    def test_partially_updates_a_todo_with_patch(self):
        payload = {"completed": True}

        response = todos_api.patch(1, payload)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["completed"] == payload["completed"]


class TestDelete:
    def test_deletes_a_todo(self):
        response = todos_api.remove(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert body["isDeleted"] is True
        assert "deletedOn" in body


@pytest.mark.negative
class TestNegativeCases:
    def test_get_by_id_with_out_of_range_id_returns_not_found(self):
        response = todos_api.get_by_id(999999)

        assert response.status_code in NOT_FOUND_STATUSES

    def test_update_with_out_of_range_id_returns_not_found(self):
        response = todos_api.update(999999, {"completed": True})

        assert response.status_code in NOT_FOUND_STATUSES

    def test_delete_with_out_of_range_id_returns_not_found(self):
        response = todos_api.remove(999999)

        assert response.status_code in NOT_FOUND_STATUSES
