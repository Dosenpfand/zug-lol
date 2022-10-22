import io
import re
from typing import TYPE_CHECKING, Tuple, Dict, Union

if TYPE_CHECKING:
    from conftest import AuthActions
    from flask.testing import FlaskClient

import pytest


# TODO
# ticket price search
# determining price for journey


class TestJourneys:
    @staticmethod
    def row_html_pattern(origin: str, destination: str, price: str) -> str:
        return (
            rf"<td>{origin}</td>(\s*)<td>{destination}</td>(\s*)<td>{price}</td>(\s*)"
            r'<td>(.*?)</td>(\s*)<td>(\s*)<form(.*?)action="/delete_journey/(?P<id>\d+)"'
        )

    @staticmethod
    def row_csv_pattern(origin: str, destination: str, price: str) -> str:
        return f"{origin},{destination},{price}"

    journeys = [
        ("Wien", "Innsbruck", "99"),
        ("Bozen", "Wels", "77"),
        ("St. Pölten", "Melk", "10"),
        ("Linz", "Berlin", "42"),
    ]

    @pytest.mark.parametrize("origin,destination,price", journeys)
    def test_add_journey(
        self,
        auth: "AuthActions",
        client: "FlaskClient",
        origin: str,
        destination: str,
        price: str,
    ) -> None:
        auth.login()
        response = client.get("/journeys")
        assert not re.search(
            self.row_html_pattern(origin, destination, price),
            response.text,
            flags=re.MULTILINE | re.DOTALL,
        )

        response = client.post(
            "/journeys",
            data=dict(
                origin=origin,
                destination=destination,
                price=price,
                date="",
                submit="Add+Journey",
            ),
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert re.search(
            self.row_html_pattern(origin, destination, price),
            response.text,
            flags=re.MULTILINE | re.DOTALL,
        )

    def test_export_journeys(self, auth: "AuthActions", client: "FlaskClient") -> bytes:
        auth.login()
        response = client.get("/export_journeys")

        for journey in self.journeys:
            assert re.search(
                self.row_csv_pattern(journey[0], journey[1], journey[2]), response.text
            )
        return response.data

    @pytest.mark.parametrize("origin,destination,price", journeys)
    def test_delete_journey(
        self,
        auth: "AuthActions",
        client: "FlaskClient",
        origin: str,
        destination: str,
        price: str,
    ) -> None:
        auth.login()
        response = client.get("/journeys")
        assert response.status_code == 200
        match = re.search(
            self.row_html_pattern(origin, destination, price),
            response.text,
            flags=re.MULTILINE | re.DOTALL,
        )
        assert match
        journey_id = match.group("id")

        response = client.post(
            f"/delete_journey/{journey_id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert not re.search(
            self.row_html_pattern(origin, destination, price),
            response.text,
            flags=re.MULTILINE | re.DOTALL,
        )

    def test_delete_all_journeys(
        self, auth: "AuthActions", client: "FlaskClient"
    ) -> None:
        auth.login()
        for journey in self.journeys:
            self.test_add_journey(auth, client, journey[0], journey[1], journey[2])

        response = client.post(
            "/journeys",
            data=dict(delete="Delete"),
            follow_redirects=True,
        )

        for journey in self.journeys:
            assert not re.search(
                self.row_html_pattern(journey[0], journey[1], journey[2]),
                response.text,
                flags=re.MULTILINE | re.DOTALL,
            )

    def test_import_journeys(self, auth: "AuthActions", client: "FlaskClient") -> None:
        auth.login()
        for journey in self.journeys:
            self.test_add_journey(auth, client, journey[0], journey[1], journey[2])
        csv_data = self.test_export_journeys(auth, client)

        response = client.post(
            "/journeys",
            data=dict(delete="Delete"),
            follow_redirects=True,
        )
        assert response.status_code == 200

        data: Dict[str, Union[str, Tuple[io.BytesIO, str]]] = dict(upload="Import")
        data["file"] = (io.BytesIO(csv_data), "exported_journeys.csv")
        response = client.post(
            "/journeys",
            data=data,
            follow_redirects=True,
            content_type="multipart/form-data",
        )

        for journey in self.journeys:
            assert re.search(
                self.row_html_pattern(journey[0], journey[1], journey[2]),
                response.text,
                flags=re.MULTILINE | re.DOTALL,
            )
