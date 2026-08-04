import pytest

from services.auth_api import auth_api

VALID_USERNAME = "emilys"
VALID_PASSWORD = "emilyspass"


@pytest.fixture(scope="session")
def valid_credentials():
    return {"username": VALID_USERNAME, "password": VALID_PASSWORD}


@pytest.fixture(scope="session")
def auth_tokens(valid_credentials):
    response = auth_api.login(**valid_credentials)
    assert response.status_code == 200, "Login must succeed to bootstrap authenticated tests"
    body = response.json()
    return {"access": body["accessToken"], "refresh": body["refreshToken"]}


@pytest.fixture(scope="session")
def auth_token(auth_tokens):
    return auth_tokens["access"]
