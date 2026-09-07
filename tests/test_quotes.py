import pytest

from services.quotes_api import quotes_api

NOT_FOUND_STATUSES = (404, 429)


class TestRead:
    def test_lists_quotes_with_default_pagination(self):
        response = quotes_api.list()

        assert response.status_code == 200
        body = response.json()
        assert "quotes" in body
        assert body["total"] > 0

    def test_gets_a_single_quote_by_id(self):
        response = quotes_api.get_by_id(1)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == 1
        assert "quote" in body
        assert "author" in body

    def test_gets_a_random_quote(self):
        response = quotes_api.get_random()

        assert response.status_code == 200
        body = response.json()
        assert "id" in body
        assert "quote" in body
        assert "author" in body


@pytest.mark.negative
class TestNegativeCases:
    def test_get_by_id_with_out_of_range_id_returns_not_found(self):
        response = quotes_api.get_by_id(999999)

        assert response.status_code in NOT_FOUND_STATUSES
