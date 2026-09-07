from services.api_client import BASE_URL, session


class QuotesApi:
    """DummyJSON's quotes resource is read-only - no add/update/delete endpoints."""

    def list(self, **params):
        return session.get(f"{BASE_URL}/quotes", params=params)

    def get_by_id(self, quote_id):
        return session.get(f"{BASE_URL}/quotes/{quote_id}")

    def get_random(self):
        return session.get(f"{BASE_URL}/quotes/random")


quotes_api = QuotesApi()
