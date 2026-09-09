import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://dummyjson.com"

# A stalled connection to the live API would otherwise hang a test
# indefinitely - requests has no session-level timeout by default, so it's
# injected here for every call unless a caller explicitly overrides it.
DEFAULT_TIMEOUT = 15

# DummyJSON enforces a hard 100-requests-per-window rate limit (verified via
# its x-ratelimit-* response headers), which this suite's size can now
# legitimately hit on ordinary reads/writes, not just the already-tolerated
# "not found" negative cases. Retrying a 429 here - transparently, on every
# call through the shared session - turns a rate-limit blip into a slower
# request instead of a flaky failure, with no changes needed in individual
# tests. Retrying writes is safe too: DummyJSON's writes are simulated and
# never persisted (see README), so a retried POST/PUT/PATCH/DELETE can't
# create a duplicate real side effect. raise_on_status=False means an
# exhausted retry still returns the final 429 response instead of raising -
# negative tests that already assert `status_code in (404, 429)` keep
# working exactly as before if the rate limit doesn't clear in time.
_rate_limit_retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=(429,),
    allowed_methods=frozenset(["GET", "POST", "PUT", "PATCH", "DELETE"]),
    respect_retry_after_header=True,
    raise_on_status=False,
)


class _TimeoutSession(requests.Session):
    def request(self, method, url, *args, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        return super().request(method, url, *args, **kwargs)


session = _TimeoutSession()
_retry_adapter = HTTPAdapter(max_retries=_rate_limit_retry)
session.mount("https://", _retry_adapter)
session.mount("http://", _retry_adapter)
