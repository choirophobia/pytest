from services.api_client import BASE_URL, session


class CommentsApi:
    def list(self, **params):
        return session.get(f"{BASE_URL}/comments", params=params)

    def get_by_id(self, comment_id):
        return session.get(f"{BASE_URL}/comments/{comment_id}")

    def get_by_post(self, post_id):
        return session.get(f"{BASE_URL}/comments/post/{post_id}")

    def create(self, payload):
        return session.post(f"{BASE_URL}/comments/add", json=payload)

    def update(self, comment_id, payload):
        return session.put(f"{BASE_URL}/comments/{comment_id}", json=payload)

    def patch(self, comment_id, payload):
        return session.patch(f"{BASE_URL}/comments/{comment_id}", json=payload)

    def remove(self, comment_id):
        return session.delete(f"{BASE_URL}/comments/{comment_id}")


comments_api = CommentsApi()
