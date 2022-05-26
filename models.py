from app import db


class Price(db.Model):
    origin = db.Column(db.Text, primary_key=True)
    destination = db.Column(db.Text, primary_key=True)
    is_vorteilscard = db.Column(db.Boolean, primary_key=True)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Price {self.price}>'
