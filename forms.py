from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class PriceForm(FlaskForm):
    origin = StringField(label='Origin', validators=[InputRequired()], render_kw={'placeholder': 'Origin (e.g. Wien)'})
    destination = StringField(label='Destination', render_kw={'placeholder': 'Destination (e.g. Innsbruck)'},
                              validators=[InputRequired()])
    submit = SubmitField(label='Search Price')
