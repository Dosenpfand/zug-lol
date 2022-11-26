import pytest
from app import create_app


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email="test@example1.com", password="test1234"):
        return self._client.post("/login", data={"email": email, "password": password})

    def logout(self):
        return self._client.get("/logout")


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SECURITY_PASSWORD_HASH": "plaintext",
        }
    )

    # other setup can go here
    yield app
    # clean up / reset resources here


@pytest.fixture()
def auth(client):
    return AuthActions(client)


@pytest.fixture()
def client(app):
    return app.test_client()


def test_request_price_form(client):
    response = client.get("/price_form")
    assert b"Ticket Price Search" in response.data


def test_request_login(auth, client):
    assert client.get("/login").status_code == 200
    response = auth.login()
    print(response.text)
    assert response.headers["Location"] == "/"
