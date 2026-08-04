from services.api_client import BASE_URL, session


class PostsApi:
    def list(self, **params):
        return session.get(f"{BASE_URL}/posts", params=params)

    def get_by_id(self, post_id):
        return session.get(f"{BASE_URL}/posts/{post_id}")

    def search(self, q):
        return session.get(f"{BASE_URL}/posts/search", params={"q": q})

    def get_by_user(self, user_id):
        return session.get(f"{BASE_URL}/posts/user/{user_id}")

    def create(self, payload):
        return session.post(f"{BASE_URL}/posts/add", json=payload)

    def update(self, post_id, payload):
        return session.put(f"{BASE_URL}/posts/{post_id}", json=payload)

    def patch(self, post_id, payload):
        return session.patch(f"{BASE_URL}/posts/{post_id}", json=payload)

    def remove(self, post_id):
        return session.delete(f"{BASE_URL}/posts/{post_id}")


posts_api = PostsApi()
