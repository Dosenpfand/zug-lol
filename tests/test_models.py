from typing import TYPE_CHECKING

from app import db

if TYPE_CHECKING:
    from flask import Flask


class TestPrice:
    def test_update_oldest_empty(self, app: "Flask") -> None:
        with app.app_context():
            from app.models import Price

            updated_prices = Price.update_oldest()
        assert not updated_prices

    def test_update_oldest_one(self, app: "Flask") -> None:
        origin = "Wien"
        destination = "Salzburg"
        with app.app_context():
            from app.models import Price

            price = Price(
                origin=origin, destination=destination, is_vorteilscard=True, price=10
            )
            db.session.add(price)
            db.session.commit()
            updated_prices = Price.update_oldest()

            assert updated_prices
            assert updated_prices[0].price > 10
            assert updated_prices[0].price < 50
