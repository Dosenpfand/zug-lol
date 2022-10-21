from flask import render_template
from flask_babel import gettext as _

from app.ticket_price.forms import PriceForm
from app.ticket_price import bp


@bp.route("/price_form", methods=["GET", "POST"])
def price_form() -> str:
    form = PriceForm()
    if form.validate_on_submit():
        return render_template("sse_container.html", form=form, title=_("Ticket Price"))
    return render_template("price_form.html", form=form, title=_("Ticket Price"))
