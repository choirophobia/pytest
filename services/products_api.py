from services.api_client import BASE_URL, session


class ProductsApi:
    def list(self, **params):
        return session.get(f"{BASE_URL}/products", params=params)

    def get_by_id(self, product_id):
        return session.get(f"{BASE_URL}/products/{product_id}")

    def search(self, q):
        return session.get(f"{BASE_URL}/products/search", params={"q": q})

    def get_categories(self):
        return session.get(f"{BASE_URL}/products/categories")

    def get_by_category(self, category):
        return session.get(f"{BASE_URL}/products/category/{category}")

    def create(self, payload):
        return session.post(f"{BASE_URL}/products/add", json=payload)

    def update(self, product_id, payload):
        return session.put(f"{BASE_URL}/products/{product_id}", json=payload)

    def patch(self, product_id, payload):
        return session.patch(f"{BASE_URL}/products/{product_id}", json=payload)

    def remove(self, product_id):
        return session.delete(f"{BASE_URL}/products/{product_id}")


products_api = ProductsApi()
