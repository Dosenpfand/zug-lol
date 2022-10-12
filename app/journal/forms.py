from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, DateField, validators, SubmitField
from wtforms.validators import InputRequired

from app.main.forms import FlexibleFloatField


class JourneyForm(FlaskForm):
    origin = StringField(
        label=_("Origin"),
        validators=[InputRequired()],
        render_kw={
            "autocomplete": "off",
            "class": "basicAutoComplete",
            "placeholder": _("e.g. Wien"),
        },
    )
    destination = StringField(
        label=_("Destination"),
        render_kw={
            "autocomplete": "off",
            "class": "basicAutoComplete",
            "placeholder": _("e.g. Innsbruck"),
        },
        validators=[InputRequired()],
    )
    price = FlexibleFloatField(
        label=_("Price in €"), render_kw={"placeholder": _("e.g. 10.5")}
    )
    date = DateField(
        label=_("Date"),
        validators=[validators.Optional()],
        render_kw={"placeholder": _("Date")},
    )
    submit = SubmitField(label=_("Add Journey"))


class DeleteJournalForm(FlaskForm):
    delete = SubmitField(label=_("Delete"), render_kw={"class": "btn btn-danger"})


class ImportJournalForm(FlaskForm):
    file = FileField(label=_("CSV File"))
    upload = SubmitField(label=_("Import"), validators=[InputRequired()])
