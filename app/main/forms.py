from flask import current_app
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, FloatField


class FlexibleFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleFloatField, self).process_formdata(valuelist)


class ProfileForm(FlaskForm):
    has_vorteilscard = BooleanField(label=_('Vorteilscard'))
    klimaticket_price = FlexibleFloatField(label=_('Klimaticket price in €'), render_kw={
        'placeholder': '{} {}'.format(_('e.g.'), current_app.config['KLIMATICKET_DEFAULT_PRICE'])})
    submit = SubmitField(label=_('Save'))
