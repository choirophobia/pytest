# DummyJSON API Tests (pytest)

An end-to-end API test suite against the live [DummyJSON](https://dummyjson.com) API, built with `pytest` and `requests`. It's a QA practice/portfolio project that demonstrates CRUD testing, auth-flow testing, and negative/error-case testing against a real HTTP API — no mocks, no local server.

This is the pytest/Python port of a sibling Jest/JavaScript suite: same target API, same resource coverage, same test cases, different stack. If you already know one, the other should feel familiar.

## Table of contents

- [Quickstart](#quickstart)
- [How it's organized](#how-its-organized)
- [The Service Object Model](#the-service-object-model)
- [Fixtures & the auth flow](#fixtures--the-auth-flow)
- [Test conventions](#test-conventions)
- [Running tests](#running-tests)
- [CI/CD: nightly run + Discord notifications](#cicd-nightly-run--discord-notifications)
- [Walkthrough: adding a new test](#walkthrough-adding-a-new-test)
- [Endpoint reference](#endpoint-reference)
- [Known quirks of the target API](#known-quirks-of-the-target-api)
- [Extending to a new resource](#extending-to-a-new-resource)

## Quickstart

Requires Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest                            # run the whole suite
```

You should see something like:

```
```

No API keys, no `.env` file, no local server to start — `tests/` talks straight to `https://dummyjson.com`.

## How it's organized

```
services/
├── api_client.py     # BASE_URL + one shared requests.Session
├── products_api.py   # ProductsApi — wraps every /products endpoint
├── users_api.py       # UsersApi   — wraps every /users endpoint
├── auth_api.py        # AuthApi    — login / me / refresh
├── carts_api.py        # CartsApi   — wraps every /carts endpoint
└── posts_api.py         # PostsApi   — wraps every /posts endpoint

tests/
├── test_products.py   # one file per resource, mirrors services/
├── test_users.py
├── test_auth.py
├── test_carts.py
└── test_posts.py

conftest.py             # shared fixtures: valid_credentials, auth_tokens, auth_token
pytest.ini              # registers the `negative` marker
```

The rule of thumb: **`services/` knows HTTP, `tests/` knows behavior.** A test file should read almost like a spec written in English, with no `requests` or URL-building logic anywhere in it.

## The Service Object Model

Tests never call `requests` or the shared `session` directly. Each resource gets a small class in `services/` that exposes its endpoints as plain Python methods:

```python
# services/products_api.py
from services.api_client import BASE_URL, session

class ProductsApi:
    def get_by_id(self, product_id):
        return session.get(f"{BASE_URL}/products/{product_id}")

    def create(self, payload):
        return session.post(f"{BASE_URL}/products/add", json=payload)
    # ...

products_api = ProductsApi()   # tests import this singleton
```

A test then reads as:

```python
response = products_api.get_by_id(1)
```

...instead of:

```python
response = session.get("https://dummyjson.com/products/1")
```

This is API testing's version of the UI world's **Page Object Model** — same idea, applied to HTTP calls instead of DOM elements. Three concrete payoffs:

| Without a service object | With a service object |
|---|---|
| Every test rebuilds the URL, method, and payload shape by hand | Tests call one readable method: `products_api.create(payload)` |
| An endpoint change means editing every test that hits it | An endpoint change means editing one method in `services/` |
| Copy-pasted request boilerplate across test files | Shared request shapes (pagination, headers, auth) live in one place |

**Rule for contributors:** if you find yourself typing `session.get(...)` or `BASE_URL` inside a file under `tests/`, stop — that logic belongs in `services/`.

Generic passthrough methods like `list(self, **params)` mean new query params — pagination, sorting, whatever the API adds — don't need a new service method at all. `products_api.list(sortBy="price", order="asc")` already works because `list()` forwards `**params` straight through; see `test_lists_products_sorted_ascending_by_price` in `tests/test_products.py` for the resulting test.

## Fixtures & the auth flow

`conftest.py` defines three session-scoped fixtures, layered so each test only asks for what it needs:

```python
valid_credentials   # {"username": "emilys", "password": "emilyspass"}
        ↓
auth_tokens         # logs in once per test session, returns {"access": ..., "refresh": ...}
        ↓
auth_token           # just the access token, for tests that only need Authorization: Bearer <token>
```

Because they're `scope="session"`, the actual `POST /auth/login` call happens **once** for the whole test run, no matter how many tests depend on it — pytest caches the fixture's return value and reuses it.

```python
def test_gets_current_user_with_valid_token(self, auth_token):
    response = auth_api.me(token=auth_token)
    assert response.status_code == 200
```

Ask for `auth_token` when you just need a bearer token, `auth_tokens` when you need the refresh token too (e.g. testing `POST /auth/refresh`), or `valid_credentials` when you need to log in yourself (e.g. testing invalid-password negative cases).

## Test conventions

- **One file per resource** — `test_<resource>.py` mirrors `services/<resource>_api.py`.
- **Group by CRUD operation**, one `class` per operation, mirroring Jest's `describe()` blocks:

  ```python
  class TestRead:      ...
  class TestCreate:    ...
  class TestUpdate:    ...
  class TestDelete:    ...

  @pytest.mark.negative
  class TestNegativeCases:  ...
  ```

- **Plain `assert`** — no assertion library needed; pytest rewrites `assert` statements to give readable failure diffs for free.
- **Assert three things per test**: status code, key response fields, and — for writes — that the echoed response actually reflects what you sent:

  ```python
  def test_creates_a_new_product(self):
      payload = {"title": "Test Product", "price": 19.99, "category": "test-category"}
      response = products_api.create(payload)

      assert response.status_code == 201
      body = response.json()
      assert body["title"] == payload["title"]
      assert body["price"] == payload["price"]
  ```

- **No state resets between tests.** DummyJSON's writes are simulated and never persisted, so there's nothing to clean up in `beforeEach`/fixture teardown.
- **Every resource has at least one negative test**: an out-of-range ID, a bad-auth case, or a missing required field.

## Running tests

```bash
pytest                                   # everything
pytest tests/test_products.py            # one file
pytest tests/test_products.py::TestCreate::test_creates_a_new_product  # one test
pytest -v                                 # verbose, one line per test
pytest -m negative                        # only negative/error-case tests
pytest -m "not negative"                  # everything except negative cases
pytest -n auto                            # parallel run (needs pytest-xdist, already in requirements.txt)
```

## CI/CD: nightly run + Discord notifications

`.github/workflows/nightly-tests.yml` runs the full suite automatically **every day at 06:00 WIB** (`0 23 * * *` in UTC — WIB is UTC+7 with no DST, so 23:00 UTC the day before lines up with 06:00 WIB), and can also be triggered manually from the Actions tab (`workflow_dispatch`).

**Pipeline steps:**

1. Checkout + install `requirements.txt`.
2. `pytest -v --json-report --json-report-file=report.json` — the [`pytest-json-report`](https://pypi.org/project/pytest-json-report/) plugin writes a structured summary (pass/fail/error/skip counts, per-test outcomes, duration) alongside the normal console output. The step uses `continue-on-error: true` so a red test run doesn't skip the notification step below.
3. `report.json` is uploaded as a build artifact (14-day retention) for when you need the full detail, not just the summary.
4. `scripts/notify_discord.py report.json` builds a Discord embed from the report and posts it to your webhook — this always runs (`if: always()`), pass or fail.
5. A final step re-fails the job if the test step failed, so the Actions tab still shows red — `continue-on-error` in step 2 only exists to let the notification step run, it doesn't hide real failures.

**The Discord message is explicitly flagged as coming from pytest** — sent under the `pytest` username, with the embed footer reading `Source: pytest · <repo> · run #<n>`, so it's unambiguous in a channel that gets messages from other bots/CI tools too. It's color-coded (green = all passed, red = any failure/error) and, on failure, lists up to 10 failing test node IDs directly in the embed.

**One-time setup required** (not something this repo can do for you):

1. In Discord: **Server Settings → Integrations → Webhooks → New Webhook**, pick the channel, copy the webhook URL.
2. In GitHub: **Repo Settings → Secrets and variables → Actions → New repository secret**, name it `DISCORD_WEBHOOK_URL`, paste the URL.

Without that secret, the workflow's test step still runs fine — only the notification step fails (loudly, in the Actions log), since a missing webhook is treated as a configuration error rather than something to silently swallow.

To test the notification path locally before relying on the schedule:

```bash
pytest --json-report --json-report-file=report.json
DISCORD_WEBHOOK_URL="<your webhook url>" python scripts/notify_discord.py report.json
```

## Walkthrough: adding a new test

Say you want to cover `GET /products/search?q=` more thoroughly. Two steps:

**1. Check the service object already has the method you need** (`services/products_api.py`):

```python
def search(self, q):
    return session.get(f"{BASE_URL}/products/search", params={"q": q})
```

It does — reuse it. If it didn't, you'd add the method here first, not inline the request in the test.

**2. Write the test** in the matching `class` in `tests/test_products.py`:

```python
class TestRead:
    def test_search_results_all_match_the_query(self):
        response = products_api.search("phone")

        assert response.status_code == 200
        body = response.json()
        for product in body["products"]:
            haystack = f"{product['title']} {product['description']}".lower()
            assert "phone" in haystack
```

That's the whole pattern: **call the service method, assert on `response.status_code` and `response.json()`.** No new imports beyond the service object, no direct HTTP calls.

## Endpoint reference

| Resource | Create | Read | Update | Delete |
|---|---|---|---|---|
| Products | `POST /products/add` | `GET /products` (+ `sortBy=`/`order=`), `/products/{id}`, `/products/search?q=`, `/products/categories`, `/products/category/{category}` | `PUT`/`PATCH /products/{id}` | `DELETE /products/{id}` |
| Users | `POST /users/add` | `GET /users`, `/users/{id}`, `/users/search?q=`, `/users/filter?key=&value=` | `PUT`/`PATCH /users/{id}` | `DELETE /users/{id}` |
| Auth | — | `POST /auth/login`, `GET /auth/me` (Bearer token) | `POST /auth/refresh` | — |
| Carts | `POST /carts/add` | `GET /carts`, `/carts/{id}`, `/carts/user/{userId}` | `PUT`/`PATCH /carts/{id}` | `DELETE /carts/{id}` |
| Posts | `POST /posts/add` | `GET /posts`, `/posts/{id}`, `/posts/search?q=`, `/posts/user/{userId}` | `PUT`/`PATCH /posts/{id}` | `DELETE /posts/{id}` |

Full docs: [dummyjson.com/docs](https://dummyjson.com/docs).

## Known quirks of the target API

These aren't bugs in the suite — they're real, verified behaviors of the live API that the tests are written to tolerate:

- **Writes don't persist.** `POST`/`PUT`/`PATCH`/`DELETE` all return a response as if the write happened (echoing your payload, or an `isDeleted`/`deletedOn` pair), but nothing is actually saved server-side. Tests assert on the response shape, not on a follow-up `GET` reflecting the change.
- **Occasional `429` instead of `404`.** Under repeated runs, "not found" lookups (and even some writes) can get rate-limited rather than cleanly 404ing. Negative tests for out-of-range IDs assert `status_code in (404, 429)` instead of a strict `== 404`.
- **`GET /auth/me` cookie fallback.** `POST /auth/login` sets `accessToken`/`refreshToken` cookies on top of returning them in the JSON body. Because all service objects share one `requests.Session` for connection reuse, a later "no token" call would silently succeed on those leftover cookies if not handled — `AuthApi.me()` explicitly clears the session's cookies when called without a token, so the "missing token" negative test is genuinely unauthenticated.
- **Invalid JWTs can return `500`.** A syntactically-invalid bearer token on `GET /auth/me` has been observed to return `500` rather than `401`/`403`. That specific negative test accepts all three (`401`, `403`, `500`).
- **ID validation isn't consistent across resources.** A non-numeric ID on `/products/{id}` returns `404` (treated as "not found"), but the same shape of request on `/users/{id}` returns `400` (treated as a malformed request). `test_products.py` and `test_users.py` each assert what their resource actually does rather than assuming the two are interchangeable — don't copy a negative-case assertion from one resource's test file into another's without checking live.
- **"No matches" isn't an error.** `GET /users/search?q=` with no hits, or `GET /users/filter` with a key that doesn't exist, both return `200` with an empty `users` array and `total: 0` — not a `404`. Same expectation applies if you add search/filter coverage for other resources.
- **Writable endpoints don't validate required fields.** `POST /users/add` with an empty `{}` payload still returns `201` with blank/`null` fields filled in — DummyJSON doesn't enforce "required" fields on create. A negative test asserting a `4xx` for a missing field would be testing behavior the API doesn't actually have.

## Extending to a new resource

To cover a resource not yet in this suite (comments, todos, quotes, recipes — see `CLAUDE.md`):

1. Confirm the exact endpoints/params in the [DummyJSON docs](https://dummyjson.com/docs).
2. Add `services/<resource>_api.py` following the existing services as a template — one method per endpoint, all going through the shared `session`.
3. Add `tests/test_<resource>.py` with `TestRead` / `TestCreate` / `TestUpdate` / `TestDelete` / `TestNegativeCases` classes.
4. Run `pytest tests/test_<resource>.py -v` and confirm real API responses match your assertions before trusting the test — DummyJSON's response shapes vary by resource (e.g. `categories` returns objects, not strings) and are worth checking with a quick `curl` first.
