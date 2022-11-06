import os
from typing import TYPE_CHECKING, Iterator

import pytest
from flask_security import hash_password

from app import create_app, init_db, security, db

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from flask import Flask
    from werkzeug.test import TestResponse

TEST_EMAIL = "test@example1.com"
TEST_PASSWORD = "password"


class AuthActions(object):
    def __init__(self, client: "FlaskClient"):
        self._client = client

    def login(
        self, email: str = TEST_EMAIL, password: str = TEST_PASSWORD
    ) -> "TestResponse":
        response = self._client.post(
            "/login",
            data=dict(email=email, password=password, submit="Login"),
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert response.request.path == "/"
        return response

    def logout(self) -> "TestResponse":
        return self._client.get("/logout")


@pytest.fixture(scope="session")
def app() -> Iterator["Flask"]:
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
        db.session.commit()

    yield app

    # TODO: Teardown (and session scope) should not be necessary, but in memory db results in error
    os.remove("app/app.db")


@pytest.fixture()
def auth(client: "FlaskClient") -> AuthActions:
    return AuthActions(client)


@pytest.fixture()
def client(app: "Flask") -> "FlaskClient":
    return app.test_client()
