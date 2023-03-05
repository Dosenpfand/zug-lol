import csv
import io
from datetime import datetime
from io import StringIO
from typing import TYPE_CHECKING, Iterator, Union

from flask import (
    flash,
    render_template,
    redirect,
    url_for,
    Response,
    stream_with_context,
    current_app,
)
from flask_babel import gettext as _
from flask_login import current_user
from flask_security import auth_required

from app import db
from app.journal import bp
from app.journal.forms import JourneyForm, DeleteJournalForm, ImportJournalForm
from app.models import Journey
from app.ticket_price.forms import PriceForm
from app.util import post_redirect

if TYPE_CHECKING:
    from werkzeug.wrappers import Response as BaseResponse

logger = current_app.logger


@bp.route("/journeys", methods=["GET", "POST"])
@auth_required()
def journeys() -> Union[str, "BaseResponse"]:
    add_journey_form = JourneyForm()
    delete_journeys_form = DeleteJournalForm()
    import_journeys_form = ImportJournalForm()

    if add_journey_form.submit.data and add_journey_form.validate():
        journey = Journey(
            user_id=current_user.id,
            origin=add_journey_form.origin.data,
            destination=add_journey_form.destination.data,
            price=add_journey_form.price.data,
            date=add_journey_form.date.data,
        )
        db.session.add(journey)
        db.session.commit()
        add_journey_form.price.raw_data = None
        add_journey_form.price.data = None
        logger.info("Journal entry added.")
        flash(_("Journal entry added."))
        return post_redirect()

    if delete_journeys_form.delete.data and delete_journeys_form.validate():
        Journey.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        logger.info("All journal entries deleted.")
        flash(_("All journal entries deleted."))
        return post_redirect()

    if import_journeys_form.upload.data and import_journeys_form.validate():
        wrapper = io.TextIOWrapper(import_journeys_form.file.data, encoding="utf-8")
        csv_reader = csv.DictReader(wrapper)

        # noinspection PyBroadException
        try:
            for row in csv_reader:
                journey = Journey(
                    user_id=current_user.id,
                    origin=row["Origin"],
                    destination=row["Destination"],
                    price=row["Price in €"],
                    date=datetime.strptime(row["Date"], "%Y-%m-%d").date(),
                )
                db.session.add(journey)
            db.session.commit()
        except UnicodeDecodeError:
            logger.error("Decode error on journal CSV upload.")
            flash(
                _("Could not decode the file. Are you sure you uploaded a CSV file?"),
                category="danger",
            )
        except KeyError as e:
            logger.error("Key error on journal CSV upload.")
            flash(
                _(
                    "Could not find the expected column {} in the uploaded CSV file.".format(
                        e
                    )
                ),
                category="danger",
            )
        except Exception:
            logger.error("Generic error on journal CSV upload.")
            flash(_("Could not process the uploaded CSV file."), category="danger")
        else:
            logger.info("Journal imported.")
            flash(_("All journal entries imported."))
        return post_redirect()

    journeys_list = (
        Journey.query.filter_by(user_id=current_user.id)
        .order_by(Journey.date.desc())
        .all()
    )

    if current_user.klimaticket_start_date:
        current_journeys = list(
            filter(
                lambda j: j.date >= current_user.klimaticket_start_date, journeys_list
            )
        )
        archived_journeys = list(
            filter(lambda j: j not in current_journeys, journeys_list)
        )
    else:
        current_journeys = journeys_list
        archived_journeys = []

    titles = [
        ("origin", _("Origin")),
        ("destination", _("Destination")),
        ("price_formatted", _("Price in €")),
        ("date_formatted", _("Date")),
    ]

    actions_title = _("Actions")
    journey_count = len(current_journeys)
    price_sum = round(sum(journey.price for journey in current_journeys), 2)
    klimaticket_gains = round(price_sum - current_user.klimaticket_price, 2)

    return render_template(
        "journeys.html",
        title=_("Travel Journal"),
        add_journey_form=add_journey_form,
        delete_journeys_form=delete_journeys_form,
        import_journeys_form=import_journeys_form,
        table=current_journeys,
        archive_table=archived_journeys,
        titles=titles,
        actions_title=actions_title,
        journey_model=Journey,
        journey_count=journey_count,
        price_sum=price_sum,
        klimaticket_gains=klimaticket_gains,
    )


@bp.route("/delete_journey/<int:journey_id>", methods=["GET", "POST"])
@auth_required()
def delete_journey(journey_id: int) -> "BaseResponse":
    journey_result = Journey.query.filter_by(id=journey_id).first()
    if journey_result and journey_result.user_id == current_user.id:
        Journey.query.filter_by(id=journey_id).delete()
        db.session.commit()
        logger.info("Journal entry deleted.")
        flash(_("Journal entry deleted."))
    else:
        logger.warning("Failed to delete journal entry.")
        flash(_("Failed to delete journal entry."))
    return redirect(url_for("journal.journeys"))


@bp.route("/export_journeys")
@auth_required()
def export_journeys() -> Response:
    def generate() -> Iterator[str]:
        data = StringIO()
        w = csv.writer(data)
        w.writerow(("Origin", "Destination", "Price in €", "Date"))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        journeys_list = Journey.query.filter_by(user_id=current_user.id).all()
        for journey in journeys_list:
            w.writerow(
                (journey.origin, journey.destination, journey.price, journey.date)
            )
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    response = Response(stream_with_context(generate()), mimetype="text/csv")
    response.headers.set(
        "Content-Disposition", "attachment", filename="exported_journeys.csv"
    )
    return response


@bp.route("/sse_container", methods=["POST"])
@auth_required()
def sse_container() -> str:
    form = PriceForm()
    form.vorteilscard.data = current_user.has_vorteilscard

    return render_template("sse_container.html", form=form, output_only_price=True)
