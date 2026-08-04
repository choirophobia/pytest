# DummyJSON API Tests (pytest)

An end-to-end API test suite against [DummyJSON](https://dummyjson.com), built with `pytest` and `requests`. This is the pytest/Python port of a sibling Jest/JavaScript suite testing the same API — same resource coverage, same test cases, different stack.

## Why the Service Object Model?

Tests never call `requests`/`session` directly — each resource has a service object (`services/products_api.py`, `services/users_api.py`, etc.) that wraps HTTP calls behind readable methods like `products_api.get_by_id(1)` or `users_api.search("Emily")`.

This is API testing's equivalent of the UI world's Page Object Model:

- **Tests read like specs, not HTTP calls.** `products_api.create(payload)` says what's happening; `session.post(f"{BASE_URL}/products/add", json=payload)` says how.
- **One place to change when the API changes.** If an endpoint path or method changes, one service method is updated instead of every test that hits it.
- **Encourages reuse over copy-paste.** Common request shapes (pagination params, search queries, auth headers) live in one method instead of being rebuilt per test.

## Project Structure

```
tests/            one file per resource, mirrors services/
services/         service objects wrapping a shared requests.Session
conftest.py       shared fixtures (session, auth tokens)
pytest.ini        markers config
```

## Running

```bash
pip install -r requirements.txt
pytest                          # run everything
pytest tests/test_products.py   # one resource
pytest -m negative              # only negative/error-case tests
pytest -m "not negative"        # everything except negative cases
pytest -v                       # verbose
```

## Notes on the target API

- DummyJSON is a live, external, already-deployed API — there's no local server and nothing is mocked.
- Writes (`POST`/`PUT`/`PATCH`/`DELETE`) are simulated: DummyJSON echoes back a response as if the write happened, but nothing is persisted server-side. Tests assert on response shape/status/echoed values, not actual persistence.
- DummyJSON has been observed to occasionally return `429` instead of `404` on "not found" lookups under repeated runs. Negative tests for out-of-range IDs assert `status_code in (404, 429)` rather than a strict equality check to avoid flaky failures.
- A malformed/invalid JWT on `GET /auth/me` has been observed to return `500` rather than `401`/`403`. That specific negative test accepts all three.
