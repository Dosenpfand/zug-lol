import os
from typing import TYPE_CHECKING, Iterator

import pytest
from flask_security import hash_password

from app import create_app, init_db

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


# TODO: Session scope should not be necessary, but in memory db results in error
# https://stackoverflow.com/questions/37908767/table-roles-users-is-already-defined-for-this-metadata-instance?answertab=modifieddesc#tab-top
@pytest.fixture(scope="session")
def app() -> Iterator["Flask"]:
    import config as app_config

    test_config = {
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECURITY_PASSWORD_HASH": "plaintext",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "BABEL_DEFAULT_LOCALE": "de",
        "FORCE_HTTPS": False,
    }
    for key, value in test_config.items():
        setattr(app_config, key, value)

    app = create_app(config=app_config)

    with app.app_context():
        init_db(drop=False)

        if not app.extensions["security"].datastore.find_user(email=TEST_EMAIL):
            app.extensions["security"].datastore.create_user(
                email=TEST_EMAIL, password=hash_password(TEST_PASSWORD), roles=[]
            )
        from app.db import db

        db.session.commit()

    yield app


@pytest.fixture()
def auth(client: "FlaskClient") -> AuthActions:
    return AuthActions(client)


@pytest.fixture()
def client(app: "Flask") -> "FlaskClient":
    return app.test_client()
