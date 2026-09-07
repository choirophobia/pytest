from services.api_client import BASE_URL, session


class RecipesApi:
    def list(self, **params):
        return session.get(f"{BASE_URL}/recipes", params=params)

    def get_by_id(self, recipe_id):
        return session.get(f"{BASE_URL}/recipes/{recipe_id}")

    def search(self, q):
        return session.get(f"{BASE_URL}/recipes/search", params={"q": q})

    def get_by_tag(self, tag):
        return session.get(f"{BASE_URL}/recipes/tag/{tag}")

    def create(self, payload):
        return session.post(f"{BASE_URL}/recipes/add", json=payload)

    def update(self, recipe_id, payload):
        return session.put(f"{BASE_URL}/recipes/{recipe_id}", json=payload)

    def patch(self, recipe_id, payload):
        return session.patch(f"{BASE_URL}/recipes/{recipe_id}", json=payload)

    def remove(self, recipe_id):
        return session.delete(f"{BASE_URL}/recipes/{recipe_id}")


recipes_api = RecipesApi()
