from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, FloatField, DateField, validators
from wtforms.validators import InputRequired
from flask import current_app


class PriceForm(FlaskForm):
    origin = StringField(label='Origin', validators=[InputRequired()],
                         render_kw={'autocomplete': 'off', 'class': 'basicAutoComplete',
                                    'placeholder': 'Origin (e.g. Wien)'})
    destination = StringField(label='Destination',
                              render_kw={'autocomplete': 'off', 'class': 'basicAutoComplete',
                                         'placeholder': 'Destination (e.g. Innsbruck)'},
                              validators=[InputRequired()])
    vorteilscard = BooleanField(label='Vorteilscard')
    submit = SubmitField(label='Search Price')


class JourneyForm(FlaskForm):
    origin = StringField(label='Origin', validators=[InputRequired()],
                         render_kw={'autocomplete': 'off', 'class': 'basicAutoComplete',
                                    'placeholder': 'e.g. Wien'})
    destination = StringField(label='Destination',
                              render_kw={'autocomplete': 'off', 'class': 'basicAutoComplete',
                                         'placeholder': 'e.g. Innsbruck'},
                              validators=[InputRequired()])
    price = FloatField(label='Price in €', validators=[validators.Optional()],
                       render_kw={'placeholder': 'e.g. 10.5 (Leave empty to auto calculate)'})
    # TODO
    date = DateField(label='Date', validators=[validators.Optional()], render_kw={'placeholder': 'Date TODO'})
    submit = SubmitField(label='Add Journey')


class ProfileForm(FlaskForm):
    has_vorteilscard = BooleanField(label='Vorteilscard')
    klimaticket_price = FloatField(label='Klimaticket price in €', render_kw={
        'placeholder': 'e.g. {}'.format(current_app.config['KLIMATICKET_DEFAULT_PRICE'])})
    submit = SubmitField(label='Save')
