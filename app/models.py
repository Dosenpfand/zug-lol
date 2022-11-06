from datetime import datetime, date

from flask import current_app
from flask_babel import format_decimal, format_date

from app import db
from time import time
from flask_security.models import fsqla_v2 as fsqla

from sqlalchemy.ext.declarative import DeclarativeMeta

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


class StationAutocomplete(BaseModel):
    input = db.Column(db.Text, primary_key=True)
    result = db.Column(db.Text)

    def __repr__(self) -> str:
        return f"StationAutocomplete({self.input}, {self.result})"


class AuthToken(BaseModel):
    # Tokens are usually valid for 300 seconds
    expires_at = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text)

    def is_valid(self, safety_margin_sec: int = 10) -> bool:
        return self.expires_at > (int(time()) + safety_margin_sec)

    def __repr__(self) -> str:
        return f"AuthToken({self.expires_at}, {self.token})>"


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

    def __repr__(self):
        return f"User({self.email}, {self.username}, {self.active}, {self.fs_uniquifier}, {self.confirmed_at})"


class Journey(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="journeys", lazy=True)
    origin = db.Column(db.Text)
    destination = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date(), default=date.today, nullable=False)

    def __repr__(self):
        return f"Journey({self.user}, {self.origin}, {self.destination}, {self.price}, {self.price})"

    @property
    def price_formatted(self) -> str:
        return format_decimal(self.price)

    @property
    def date_formatted(self) -> str:
        return format_date(self.date)
