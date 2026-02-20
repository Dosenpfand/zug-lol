import os
import re
from datetime import datetime, timedelta

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

    def test_get_price_for_route_with_few_prices(self) -> None:
        """Only few connections for this route have prices"""
        origin = "Moosburg in Ktn Ortsmitte"
        destination = "Klagenfurt Heuplatz "

        today = datetime.now()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = (today + timedelta(days=days_ahead)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )

        price = get_price(
            origin, destination, date=next_monday, has_vc66=True, take_median=True
        )

        assert price
        assert price > 0
        assert price < 50
