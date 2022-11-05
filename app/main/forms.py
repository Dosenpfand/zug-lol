from typing import List, Optional

from flask import current_app
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, FloatField, DateField, validators
from wtforms.validators import NoneOf


class FlexibleFloatField(FloatField):
    def process_formdata(self, valuelist: List[str]) -> Optional[float]:
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleFloatField, self).process_formdata(valuelist)


class ProfileForm(FlaskForm):
    has_vorteilscard = BooleanField(label=_("Vorteilscard"))
    klimaticket_price = FlexibleFloatField(
        label=_("Klimaticket price in €"),
        render_kw={
            "placeholder": "{} {}".format(
                _("e.g."), current_app.config["KLIMATICKET_DEFAULT_PRICE"]
            )
        },
    )
    klimaticket_start_date = DateField(
        label=_("Klimaticket start date"), validators=[validators.Optional()]
    )
    submit = SubmitField(label=_("Save"))


class DeleteAccountForm(FlaskForm):
    is_sure = BooleanField(
        label=_("Do you really want to delete your account?"),
        validators=[NoneOf([False], message=_("Needs to be selected"))],
    )
    submit = SubmitField(label=_("Delete account"))
