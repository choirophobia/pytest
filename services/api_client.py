import requests

BASE_URL = "https://dummyjson.com"

# A stalled connection to the live API would otherwise hang a test
# indefinitely - requests has no session-level timeout by default, so it's
# injected here for every call unless a caller explicitly overrides it.
DEFAULT_TIMEOUT = 15


class _TimeoutSession(requests.Session):
    def request(self, method, url, *args, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        return super().request(method, url, *args, **kwargs)


session = _TimeoutSession()
