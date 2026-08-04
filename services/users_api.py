from services.api_client import BASE_URL, session


class UsersApi:
    def list(self, **params):
        return session.get(f"{BASE_URL}/users", params=params)

    def get_by_id(self, user_id):
        return session.get(f"{BASE_URL}/users/{user_id}")

    def search(self, q):
        return session.get(f"{BASE_URL}/users/search", params={"q": q})

    def filter(self, key, value):
        return session.get(f"{BASE_URL}/users/filter", params={"key": key, "value": value})

    def create(self, payload):
        return session.post(f"{BASE_URL}/users/add", json=payload)

    def update(self, user_id, payload):
        return session.put(f"{BASE_URL}/users/{user_id}", json=payload)

    def patch(self, user_id, payload):
        return session.patch(f"{BASE_URL}/users/{user_id}", json=payload)

    def remove(self, user_id):
        return session.delete(f"{BASE_URL}/users/{user_id}")


users_api = UsersApi()
