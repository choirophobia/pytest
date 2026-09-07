from services.api_client import BASE_URL, session


class TodosApi:
    def list(self, **params):
        return session.get(f"{BASE_URL}/todos", params=params)

    def get_by_id(self, todo_id):
        return session.get(f"{BASE_URL}/todos/{todo_id}")

    def get_random(self):
        return session.get(f"{BASE_URL}/todos/random")

    def get_by_user(self, user_id):
        return session.get(f"{BASE_URL}/todos/user/{user_id}")

    def create(self, payload):
        return session.post(f"{BASE_URL}/todos/add", json=payload)

    def update(self, todo_id, payload):
        return session.put(f"{BASE_URL}/todos/{todo_id}", json=payload)

    def patch(self, todo_id, payload):
        return session.patch(f"{BASE_URL}/todos/{todo_id}", json=payload)

    def remove(self, todo_id):
        return session.delete(f"{BASE_URL}/todos/{todo_id}")


todos_api = TodosApi()
