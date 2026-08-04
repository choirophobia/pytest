# DummyJSON API Testing — Pytest E2E Suite

## Project Context
- Goal: build a complete end-to-end API test suite against DummyJSON (https://dummyjson.com) using pytest.
- Purpose: QA practice/portfolio piece demonstrating CRUD testing, auth flow testing, and negative/error-case testing.
- Target API: external, already-running (DummyJSON) — no local server, no mocking. Use the `requests` library for HTTP calls.
- No API key required. CORS enabled (irrelevant server-side, but noted for parity with the JS version). Writes are simulated (not persisted) — assertions should check response shape/status/echoed values, not actual state persistence.

## Tech Stack
- Test runner: pytest
- HTTP client: requests (`requests.Session` for connection reuse)
- Language: Python 3.11+
- Optional but recommended: `pytest-xdist` (parallel runs), `python-dotenv` (if credentials ever move to env vars)

## Project Structure
```
dummyjson-api-tests-pytest/
├── tests/
│   ├── test_products.py
│   ├── test_users.py
│   ├── test_auth.py
│   ├── test_carts.py
│   └── test_posts.py
├── services/
│   ├── api_client.py       # shared requests.Session / base URL config
│   ├── products_api.py     # service object wrapping /products endpoints
│   ├── users_api.py        # service object wrapping /users endpoints
│   ├── auth_api.py         # service object wrapping /auth endpoints
│   ├── carts_api.py        # service object wrapping /carts endpoints
│   └── posts_api.py        # service object wrapping /posts endpoints
├── conftest.py              # shared fixtures (session, auth token, etc.)
├── pytest.ini                # pytest config (markers, test paths)
├── requirements.txt
├── README.md
└── CLAUDE.md
```

Tests call resource-specific service objects (e.g. `products_api.get_by_id(1)`), never `api_client`/`requests` directly — the Service Object Model, API testing's equivalent of the Page Object Model. See README.md for the full rationale (port from the Jest version's README).

## Commands
- Install: `pip install -r requirements.txt` (or `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`)
- Run all tests: `pytest`
- Run one file: `pytest tests/test_products.py`
- Run one test: `pytest tests/test_products.py::test_creates_a_new_product`
- Verbose output: `pytest -v`
- Run by marker: `pytest -m negative`
- Watch mode (requires `pytest-watch`): `ptw`

## Conventions
- One test file per resource (`test_products.py`, `test_users.py`, `test_carts.py`, `test_posts.py`, plus `test_comments.py`, `test_todos.py`, `test_quotes.py`, `test_recipes.py` as coverage expands).
- Group tests with a `class Test<Operation>:` per CRUD operation (`TestCreate` / `TestRead` / `TestUpdate` / `TestDelete`) plus a `TestNegativeCases` class per resource — this mirrors Jest's `describe()` nesting since pytest classes don't need `self` state to group tests logically.
- Use a `@pytest.mark.negative` marker (registered in `pytest.ini`) on negative-case tests so they can be run/excluded independently (`pytest -m negative`, `pytest -m "not negative"`).
- Use `conftest.py` fixtures only for shared setup (e.g. a session-scoped `auth_token` fixture), not for resetting state — DummyJSON doesn't persist writes, so there's nothing to reset between tests.
- Assertion style: check `response.status_code`, key fields in `response.json()`, and — for writes — that the echoed response reflects the payload sent. Prefer plain `assert` statements (pytest rewrites them for readable failure output — no need for a separate assertion library).
- Always include at least one negative test per resource: invalid ID (e.g. out-of-range like 999999), missing required field, invalid auth. Where DummyJSON is known to occasionally rate-limit "not found" lookups, assert `response.status_code in (404, 429)` rather than a strict `== 404` (see Notes).

## Resource Endpoint Reference

### Products
- CREATE: `POST /products/add`
- READ: `GET /products`, `GET /products/{id}`, `GET /products/search?q=`, `GET /products/category/{category}`, `GET /products/categories`
- UPDATE: `PUT /products/{id}`, `PATCH /products/{id}`
- DELETE: `DELETE /products/{id}`

### Users
- CREATE: `POST /users/add`
- READ: `GET /users`, `GET /users/{id}`, `GET /users/search?q=`, `GET /users/filter`
- UPDATE: `PUT /users/{id}`, `PATCH /users/{id}`
- DELETE: `DELETE /users/{id}`

### Auth
- `POST /auth/login` — returns access/refresh tokens
- `GET /auth/me` — requires Bearer token
- `POST /auth/refresh` — refresh access token

### Carts
- CREATE: `POST /carts/add`
- READ: `GET /carts`, `GET /carts/{id}`, `GET /carts/user/{userId}`
- UPDATE: `PUT /carts/{id}`, `PATCH /carts/{id}`
- DELETE: `DELETE /carts/{id}`

### Posts / Comments / Todos / Quotes / Recipes
- Follow the same CRUD pattern as products/users (list, single, search where available, add, update, delete). Confirm exact query params in https://dummyjson.com/docs before writing tests.

## Service Object Pattern (Python)

Each service module wraps a shared `requests.Session` behind readable methods, e.g.:

```python
# services/products_api.py
from services.api_client import BASE_URL, session

class ProductsApi:
    def list(self, **params):
        return session.get(f"{BASE_URL}/products", params=params)

    def get_by_id(self, product_id):
        return session.get(f"{BASE_URL}/products/{product_id}")

    def search(self, q):
        return session.get(f"{BASE_URL}/products/search", params={"q": q})

    def create(self, payload):
        return session.post(f"{BASE_URL}/products/add", json=payload)

    def update(self, product_id, payload):
        return session.put(f"{BASE_URL}/products/{product_id}", json=payload)

    def patch(self, product_id, payload):
        return session.patch(f"{BASE_URL}/products/{product_id}", json=payload)

    def remove(self, product_id):
        return session.delete(f"{BASE_URL}/products/{product_id}")

products_api = ProductsApi()
```

`services/api_client.py` sets `BASE_URL = "https://dummyjson.com"` and a module-level `session = requests.Session()`. Unlike axios's `validateStatus`, `requests` never raises on 4xx/5xx by default — `response.raise_for_status()` is opt-in — so no extra config is needed to assert directly on `response.status_code`.

## Testing Priorities (build in this order)
1. Products — full CRUD + search/filter + negative cases (most documented, good starting point)
2. Users — full CRUD + search/filter
3. Auth — login, protected route with/without token, token refresh
4. Carts — CRUD tied to a user ID
5. Remaining resources (posts, comments, todos, quotes, recipes) — lighter coverage, reuse patterns from above

## Notes
- No self-hosted server involved — this is an external, already-deployed API, so there's no equivalent of Supertest's app-binding needed.
- Rate limits: none officially documented for DummyJSON, but "not found" negative-case lookups (out-of-range IDs) have been observed to occasionally return `429` instead of `404` under repeated runs. Assert `response.status_code in (404, 429)` for those specific cases rather than a strict equality check, to avoid flaky failures — this mirrors a fix already applied in the Jest version of this suite.
- This project is for practice/portfolio use — treat DummyJSON as a dev/testing aid, not production infrastructure.
