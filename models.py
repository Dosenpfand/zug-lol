from datetime import datetime

from app import db
from time import time


class Price(db.Model):
    origin = db.Column(db.Text, primary_key=True)
    destination = db.Column(db.Text, primary_key=True)
    is_vorteilscard = db.Column(db.Boolean, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Price {self.price}>'


class AuthToken(db.Model):
    # Tokens are usually valid for 300 seconds
    expires_at = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text)

    def is_valid(self, safety_margin_sec=10):
        return self.expires_at > (int(time()) + safety_margin_sec)

    def __repr__(self):
        return f'<AuthToken {self.expires_at}>'