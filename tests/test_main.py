import pytest
from flask_security import hash_password

from app import create_app, init_db, security


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email="test@example1.com", password="test1234"):
        return self._client.post(
            "/login", data={"email": email, "password": password, "submit": "Login"}
        )

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
            "SQLALCHEMY_DATABASE_URI": "sqlite:///app.db",
        }
    )

    with app.app_context():
        init_db(drop=False)

        if not security.datastore.find_user(email="test@example1.com"):
            security.datastore.create_user(
                email="test@example1.com", password=hash_password("password"), roles=[]
            )
        security.datastore.db.session.commit()

    yield app
    # TODO: clean up


@pytest.fixture()
def auth(client):
    return AuthActions(client)


@pytest.fixture()
def client(app):
    return app.test_client()


def test_request_price_form(client):
    response = client.get("/price_form")
    assert b"<form" in response.data


def test_login_wrong_credentials(auth, client):
    assert client.get("/login").status_code == 200
    response = auth.login()
    assert response.status_code == 200
    assert "Ungültiges Passwort" in response.text
