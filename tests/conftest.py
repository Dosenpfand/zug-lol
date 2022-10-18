import pytest
from flask_security import hash_password

from app import create_app, init_db, security

TEST_EMAIL = "test@example1.com"
TEST_PASSWORD = "password"


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email=TEST_EMAIL, password=TEST_PASSWORD):
        response = self._client.post(
            "/login",
            data=dict(email=email, password=password, submit="Login"),
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert response.request.path == "/"
        return response

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

        if not security.datastore.find_user(email=TEST_EMAIL):
            security.datastore.create_user(
                email=TEST_EMAIL, password=hash_password(TEST_PASSWORD), roles=[]
            )
        security.datastore.db.session.commit()

    yield app


@pytest.fixture()
def auth(client):
    return AuthActions(client)


@pytest.fixture()
def client(app):
    return app.test_client()
