from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, FloatField, DateField, validators, DecimalField
from wtforms.validators import InputRequired
from flask import current_app


class PriceForm(FlaskForm):
    origin = StringField(label=_('Origin'), validators=[InputRequired()],
                         render_kw={'autocomplete': 'off', 'class': 'basicAutoComplete',
                                    'placeholder': _('Origin (e.g. Wien)')})
    destination = StringField(label=_('Destination'),
                              render_kw={'autocomplete': 'off', 'class': 'basicAutoComplete',
                                         'placeholder': _('Destination (e.g. Innsbruck)')},
                              validators=[InputRequired()])
    vorteilscard = BooleanField(label=_('Vorteilscard'))
    submit = SubmitField(label=_('Search Price'))


class JourneyForm(FlaskForm):
    class Meta:
        locales = current_app.config['LANGUAGES']

    origin = StringField(label=_('Origin'), validators=[InputRequired()],
                         render_kw={'autocomplete': 'off', 'class': 'basicAutoComplete',
                                    'placeholder': _('Origin (e.g. Wien)')})
    destination = StringField(label=_('Destination'),
                              render_kw={'autocomplete': 'off', 'class': 'basicAutoComplete',
                                         'placeholder': _('Destination (e.g. Innsbruck)')},
                              validators=[InputRequired()])
    price = DecimalField(use_locale=True, label=_('Price in €'), render_kw={'placeholder': _('e.g. 10.5')})
    date = DateField(label=_('Date'), validators=[validators.Optional()], render_kw={'placeholder': _('Date')})
    submit = SubmitField(label=_('Add Journey'))


class ProfileForm(FlaskForm):
    class Meta:
        locales = current_app.config['LANGUAGES']

    has_vorteilscard = BooleanField(label=_('Vorteilscard'))
    klimaticket_price = DecimalField(use_locale=True, label=_('Klimaticket price in €'), render_kw={
        'placeholder': '{} {}'.format(_('e.g.'), current_app.config['KLIMATICKET_DEFAULT_PRICE'])})
    submit = SubmitField(label=_('Save'))


class DeleteJournalForm(FlaskForm):
    delete = SubmitField(label=_('Delete'), render_kw={'class': 'btn btn-danger'})
