from services.api_client import BASE_URL, session


class CartsApi:
    def list(self, **params):
        return session.get(f"{BASE_URL}/carts", params=params)

    def get_by_id(self, cart_id):
        return session.get(f"{BASE_URL}/carts/{cart_id}")

    def get_by_user(self, user_id):
        return session.get(f"{BASE_URL}/carts/user/{user_id}")

    def create(self, payload):
        return session.post(f"{BASE_URL}/carts/add", json=payload)

    def update(self, cart_id, payload):
        return session.put(f"{BASE_URL}/carts/{cart_id}", json=payload)

    def patch(self, cart_id, payload):
        return session.patch(f"{BASE_URL}/carts/{cart_id}", json=payload)

    def remove(self, cart_id):
        return session.delete(f"{BASE_URL}/carts/{cart_id}")


carts_api = CartsApi()
