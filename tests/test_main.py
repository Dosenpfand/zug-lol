from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from conftest import AuthActions
    from flask.testing import FlaskClient

from conftest import TEST_EMAIL, TEST_PASSWORD


class TestJourneys:
    places = ["wien", "linz", "salzburg", "innsbruck"]

    @pytest.mark.parametrize("place", places)
    def test_station_autocomplete(self, client: "FlaskClient", place: str) -> None:
        response = client.get(f"/station_autocomplete?q={place}")
        assert response.is_json
        assert isinstance(response.json, list)
        for result in response.json:
            assert place.lower() in result.lower()

    def test_profile_view(self, auth: "AuthActions", client: "FlaskClient") -> None:
        auth.login()
        response = client.get("/profile")
        assert TEST_EMAIL in response.text

    def test_account_delete(self, auth: "AuthActions", client: "FlaskClient") -> None:
        auth.login()

        response = client.post(
            "/delete_account",
            data=dict(is_sure="y", submit="Konto+löschen"),
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert response.request.path == "/"

        response = client.post(
            "/login",
            data=dict(email=TEST_EMAIL, password=TEST_PASSWORD, submit="Login"),
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert response.request.path == "/login"
