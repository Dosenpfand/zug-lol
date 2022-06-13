from datetime import datetime, date

from flask import current_app

from app import db
from time import time
from flask_security.models import fsqla_v2 as fsqla


class Price(db.Model):
    origin = db.Column(db.Text, primary_key=True)
    destination = db.Column(db.Text, primary_key=True)
    is_vorteilscard = db.Column(db.Boolean, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Price {self.price}>'


class StationAutocomplete(db.Model):
    input = db.Column(db.Text, primary_key=True)
    result = db.Column(db.Text)

    def __repr__(self):
        return f'<StationAutocomplete {self.input}>'


class AuthToken(db.Model):
    # Tokens are usually valid for 300 seconds
    expires_at = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text)

    def is_valid(self, safety_margin_sec=10):
        return self.expires_at > (int(time()) + safety_margin_sec)

    def __repr__(self):
        return f'<AuthToken {self.expires_at}>'


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    has_vorteilscard = db.Column(db.Boolean, default=False)
    klimaticket_price = db.Column(db.Float, default=current_app.config['KLIMATICKET_DEFAULT_PRICE'])
    journeys = db.relationship('Journey', back_populates='user', lazy=True)


class Journey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: when moved to postgres
    # id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='journeys', lazy=True)
    origin = db.Column(db.Text)
    destination = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date(), default=date.today)
