import os
import re

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from flask import Flask


class TestUtil:
    @staticmethod
    def result_html_pattern(origin: str, destination: str) -> str:
        return (
            rf"<p>Price for a ticket from {origin} to {destination}:</p>"
            rf'<p><mark class="display-4">(?P<price>(\d+([\.,]))?\d+) €</mark></p>'
        )

    def test_sse(self, app: "Flask") -> None:
        origin = "Wien"
        destination = "St. Pölten"
        with app.app_context():
            from util.sse import get_price_generator  # noqa

            output = [
                x for x in get_price_generator(origin, destination, has_vc66=False)
            ]

        match = re.search(
            self.result_html_pattern(origin, destination),
            output[-1],
            flags=re.MULTILINE | re.DOTALL,
        )
        print(output)
        assert match
        price = float(match.group("price").replace(",", "."))
        assert price > 5
        assert price < 50

    # TODO: Teardown (and whole class) should not be necessary, but in memory db results in error
    @staticmethod
    def teardown_class() -> None:
        os.remove("app/app.db")
