import os
import re

from typing import TYPE_CHECKING

from util.oebb import get_price

if TYPE_CHECKING:
    from flask import Flask


class TestUtil:
    @staticmethod
    def result_html_pattern(origin: str, destination: str) -> str:
        return (
            rf"<p>((Price for a ticket from)|(Preis für ein Ticket von)) {origin} ((nach)|(to)) {destination}:</p>"
            rf'<p><mark class="display-4">(?P<price>(\d+([\.,]))?\d+) €</mark></p>'
        )

    def test_sse(self, app: "Flask") -> None:
        origin = "Wien"
        destination = "Amstetten"
        with app.app_context():
            from app.util import get_price_generator

            output = [
                x for x in get_price_generator(origin, destination, has_vc66=False)
            ]

        match = re.search(
            self.result_html_pattern(origin, destination),
            output[-1],
            flags=re.MULTILINE | re.DOTALL,
        )
        assert match
        price = float(match.group("price").replace(",", "."))
        assert price > 5
        assert price < 50

    def test_get_price(self) -> None:
        origin = "Wien"
        destination = "Amstetten"
        price = get_price(origin, destination, has_vc66=True, take_median=True)

        assert price
        assert price > 5
        assert price < 50
