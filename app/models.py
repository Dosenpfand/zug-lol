from datetime import datetime, date
from typing import Optional, List

import jwt
from flask import current_app
from flask_babel import format_decimal, format_date

from app import db
from time import time
from flask_security.models import fsqla_v2 as fsqla

from sqlalchemy.ext.declarative import DeclarativeMeta

from util.oebb import get_price, get_access_token

# NOTE: Needed for mypy
BaseModel: DeclarativeMeta = db.Model


class Price(BaseModel):
    origin = db.Column(db.Text, primary_key=True)
    destination = db.Column(db.Text, primary_key=True)
    is_vorteilscard = db.Column(db.Boolean, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Price({self.origin}, {self.destination}, {self.is_vorteilscard}, {self.price}, {self.updated})"

    @classmethod
    def get_oldest(
        cls, count: int = 1, min_update_time: Optional[datetime] = None
    ) -> Optional[List["Price"]]:
        current_query = cls.query
        current_query = (
            current_query.filter(cls.updated < min_update_time)
            if min_update_time
            else current_query
        )

        return current_query.order_by(Price.updated.asc()).limit(count).all()

    @classmethod
    def update_oldest(
        cls, count: int = 1, min_update_time: Optional[datetime] = None
    ) -> Optional[List["Price"]]:
        price_objs = cls.get_oldest(count, min_update_time)
        if not price_objs:
            return None

        access_token = AuthToken.get_valid_one()
        for price_obj in price_objs:
            price = get_price(
                price_obj.origin,
                price_obj.destination,
                has_vc66=price_obj.is_vorteilscard,
                take_median=True,
                access_token=access_token,
            )

            if price:
                price_obj.price = price
                price_obj.updated = datetime.utcnow()

        db.session.commit()
        return price_objs


class StationAutocomplete(BaseModel):
    input = db.Column(db.Text, primary_key=True)
    result = db.Column(db.Text)

    def __repr__(self) -> str:
        return f"StationAutocomplete({self.input}, {self.result})"


class AuthToken(BaseModel):
    # Tokens are usually valid for 300 seconds
    expires_at = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text)

    def __repr__(self) -> str:
        return f"AuthToken({self.expires_at}, {self.token})>"

    def is_valid(self, safety_margin_sec: int = 10) -> bool:
        return self.expires_at > (int(time()) + safety_margin_sec)

    @classmethod
    def get_valid_one(cls) -> Optional[str]:
        current_token: AuthToken = cls.query.first()

        if current_token and current_token.is_valid():
            return current_token.token

        access_token = get_access_token()

        if not access_token:
            return None

        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        expires_at = decoded_token["exp"]

        # TODO: Update instead of delete, create?
        if current_token:
            db.session.delete(current_token)

        new_token = AuthToken(token=access_token, expires_at=expires_at)
        db.session.add(new_token)
        db.session.commit()
        return access_token


class Role(BaseModel, fsqla.FsRoleMixin):
    def __repr__(self) -> str:
        return f"Role({self.name}, {self.description}, {self.permissions}, {self.update_datetime})"


class User(BaseModel, fsqla.FsUserMixin):
    has_vorteilscard = db.Column(db.Boolean, default=True)
    klimaticket_price = db.Column(
        db.Float, default=current_app.config["KLIMATICKET_DEFAULT_PRICE"]
    )
    klimaticket_start_date = db.Column(db.Date, default=date.today, nullable=True)
    journeys = db.relationship(
        "Journey", back_populates="user", cascade="all, delete-orphan", lazy=True
    )
    language = db.Column(
        db.String(length=255), default=current_app.config["BABEL_DEFAULT_LOCALE"]
    )

    def __repr__(self) -> str:
        return f"User({self.email}, {self.username}, {self.active}, {self.fs_uniquifier}, {self.confirmed_at})"


class Journey(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="journeys", lazy=True)
    origin = db.Column(db.Text)
    destination = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date(), default=date.today, nullable=False)

    def __repr__(self) -> str:
        return f"Journey({self.user}, {self.origin}, {self.destination}, {self.price}, {self.price})"

    @property
    def price_formatted(self) -> str:
        return format_decimal(self.price)

    @property
    def date_formatted(self) -> str:
        return format_date(self.date)
