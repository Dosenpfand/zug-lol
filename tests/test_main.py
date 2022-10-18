from conftest import TEST_EMAIL, TEST_PASSWORD


class TestJourneys:
    def test_profile_view(self, auth, client):
        auth.login()
        response = client.get("/profile")
        assert TEST_EMAIL in response.text

    def test_account_delete(self, auth, client):
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
