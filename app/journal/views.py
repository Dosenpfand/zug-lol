import csv
import io
from io import StringIO

from flask import (
    flash,
    render_template,
    redirect,
    url_for,
    Response,
    stream_with_context,
)
from flask_babel import gettext as _, format_decimal, format_date
from flask_login import current_user
from flask_security import auth_required

from app import db
from app.ticket_price.forms import PriceForm
from app.journal.forms import JourneyForm, DeleteJournalForm, ImportJournalForm
from app.models import Journey
from app.journal import bp


@bp.route("/journeys", methods=["GET", "POST"])
@auth_required()
def journeys():
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
        flash(_("Journal entry added."))

    if delete_journeys_form.delete.data and delete_journeys_form.validate():
        Journey.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash(_("All journal entries deleted."))

    if import_journeys_form.upload.data and import_journeys_form.validate():
        wrapper = io.TextIOWrapper(import_journeys_form.file.data, encoding="utf-8")
        csv_reader = csv.DictReader(wrapper)

        try:
            for row in csv_reader:
                journey = Journey(
                    user_id=current_user.id,
                    origin=row["Origin"],
                    destination=row["Destination"],
                    price=row["Price in €"],
                    date=row["Date"],
                )
                db.session.add(journey)
            db.session.commit()
        except UnicodeDecodeError:
            flash(
                _("Could not decode the file. Are you sure you uploaded a CSV file?"),
                category="danger",
            )
        except KeyError as e:
            flash(
                _(
                    "Could not find the expected column {} in the uploaded CSV file.".format(
                        e
                    )
                ),
                category="danger",
            )
        except Exception:
            flash(_("Could not process the uploaded CSV file."), category="danger")
        else:
            flash(_("All journal entries imported."))

    journeys_objs = (
        Journey.query.filter_by(user_id=current_user.id)
        .order_by(Journey.date.desc())
        .all()
    )

    journey_dicts = []
    for journey_obj in journeys_objs:
        journey_dict = {
            "id": journey_obj.id,
            "origin": journey_obj.origin,
            "destination": journey_obj.destination,
            "price": format_decimal(journey_obj.price),
            "date": format_date(journey_obj.date),
        }
        journey_dicts.append(journey_dict)

    titles = [
        ("origin", _("Origin")),
        ("destination", _("Destination")),
        ("price", _("Price in €")),
        ("date", _("Date")),
    ]
    actions_title = _("Actions")
    journey_count = len(journeys_objs)
    price_sum = round(sum(journey.price for journey in journeys_objs), 2)
    klimaticket_gains = round(price_sum - current_user.klimaticket_price, 2)

    return render_template(
        "journeys.html",
        title=_("Travel Journal"),
        add_journey_form=add_journey_form,
        delete_journeys_form=delete_journeys_form,
        import_journeys_form=import_journeys_form,
        table=journey_dicts,
        titles=titles,
        actions_title=actions_title,
        journey_model=Journey,
        journey_count=journey_count,
        price_sum=price_sum,
        klimaticket_gains=klimaticket_gains,
    )


@bp.route("/delete_journey/<int:journey_id>", methods=["GET", "POST"])
@auth_required()
def delete_journey(journey_id):
    journey_result = Journey.query.filter_by(id=journey_id).first()
    if journey_result and journey_result.user_id == current_user.id:
        Journey.query.filter_by(id=journey_id).delete()
        db.session.commit()
        flash(_("Journal entry deleted."))
    else:
        flash(_("Failed to delete journal entry."))
    return redirect(url_for("journal.journeys"))


@bp.route("/export_journeys")
@auth_required()
def export_journeys():
    def generate():
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
def sse_container():
    form = PriceForm()
    form.vorteilscard.data = current_user.has_vorteilscard

    return render_template("sse_container.html", form=form, output_only_price=True)
