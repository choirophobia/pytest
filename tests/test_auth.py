import pytest

from services.auth_api import auth_api

# DummyJSON returns 500 (instead of 401/403) for a syntactically-invalid
# JWT signature, so negative "protected route" checks accept the wider range.
UNAUTHORIZED_STATUSES = (401, 403, 500)


class TestLogin:
    def test_logs_in_with_valid_credentials(self, valid_credentials):
        response = auth_api.login(**valid_credentials)

        assert response.status_code == 200
        body = response.json()
        assert body["username"] == valid_credentials["username"]
        assert "accessToken" in body
        assert "refreshToken" in body

    def test_login_response_includes_user_profile_fields(self, valid_credentials):
        response = auth_api.login(**valid_credentials)

        assert response.status_code == 200
        body = response.json()
        assert "id" in body
        assert "email" in body
        assert "firstName" in body
        assert "lastName" in body


class TestProtectedRoute:
    def test_gets_current_user_with_valid_token(self, auth_token, valid_credentials):
        response = auth_api.me(token=auth_token)

        assert response.status_code == 200
        body = response.json()
        assert body["username"] == valid_credentials["username"]

    def test_gets_current_user_rejects_missing_token(self):
        response = auth_api.me(token=None)

        assert response.status_code == 401

    def test_gets_current_user_rejects_invalid_token(self):
        response = auth_api.me(token="this.is.not-a-valid-token")

        assert response.status_code in UNAUTHORIZED_STATUSES


class TestTokenRefresh:
    def test_refreshes_the_access_token(self, auth_tokens):
        response = auth_api.refresh(auth_tokens["refresh"])

        assert response.status_code == 200
        body = response.json()
        assert "accessToken" in body
        assert "refreshToken" in body

    def test_refreshed_token_grants_access_to_protected_route(self, auth_tokens):
        refresh_response = auth_api.refresh(auth_tokens["refresh"])
        new_access_token = refresh_response.json()["accessToken"]

        me_response = auth_api.me(token=new_access_token)

        assert me_response.status_code == 200


@pytest.mark.negative
class TestNegativeCases:
    def test_login_with_invalid_password_is_rejected(self, valid_credentials):
        response = auth_api.login(valid_credentials["username"], "wrong-password")

        assert response.status_code == 400

    def test_login_with_unknown_username_is_rejected(self):
        response = auth_api.login("no-such-user", "whatever")

        assert response.status_code == 400

    def test_login_with_missing_password_is_rejected(self, valid_credentials):
        response = auth_api.login_raw({"username": valid_credentials["username"]})

        assert response.status_code == 400
