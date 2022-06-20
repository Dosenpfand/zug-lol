from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import InputRequired


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
