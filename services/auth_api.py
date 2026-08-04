from services.api_client import BASE_URL, session


class AuthApi:
    def login(self, username, password, expires_in_mins=None):
        payload = {"username": username, "password": password}
        if expires_in_mins is not None:
            payload["expiresInMins"] = expires_in_mins
        return session.post(f"{BASE_URL}/auth/login", json=payload)

    def login_raw(self, payload):
        return session.post(f"{BASE_URL}/auth/login", json=payload)

    def me(self, token=None):
        # /auth/login sets accessToken/refreshToken cookies on the shared session,
        # and DummyJSON accepts those as a fallback when no Authorization header is
        # sent. Clear them so a "no token" call is genuinely unauthenticated instead
        # of silently riding on a previous login in the same session.
        if token is None:
            session.cookies.clear()
            return session.get(f"{BASE_URL}/auth/me")
        return session.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})

    def refresh(self, refresh_token, expires_in_mins=None):
        payload = {"refreshToken": refresh_token}
        if expires_in_mins is not None:
            payload["expiresInMins"] = expires_in_mins
        return session.post(f"{BASE_URL}/auth/refresh", json=payload)


auth_api = AuthApi()
