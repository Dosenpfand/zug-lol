import csv
from io import StringIO
from json import dumps

from flask import render_template, Blueprint, Response, stream_with_context, request, flash
from flask_security import auth_required, current_user

from forms import PriceForm, JourneyForm, ProfileForm, DeleteJournalForm
from models import Journey, User, StationAutocomplete
from util.auth_token import get_valid_access_token
from util.oebb import get_station_names
from util.sse import get_price_generator
from app import db

ticket_price = Blueprint('ticket_price', __name__, template_folder='templates')


@ticket_price.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@ticket_price.route('/price_form', methods=['GET', 'POST'])
def price_form():
    form = PriceForm()
    if form.validate_on_submit():
        return render_template('sse_container.html', form=form)
    return render_template('price_form.html', form=form)


@ticket_price.route('/get_price')
def get_price():
    origin = request.args.get('origin', type=str)
    destination = request.args.get('destination', type=str)
    has_vorteilscard = request.args.get('vorteilscard', type=str, default='False') == 'True'
    output_only_price = request.args.get('output_only_price', type=bool, default='False')

    return Response(stream_with_context(
        get_price_generator(origin, destination, has_vc66=has_vorteilscard, output_only_price=output_only_price)),
        mimetype='text/event-stream')


@ticket_price.route('/station_autocomplete')
def station_autocomplete():
    name = request.args.get('q')

    if not name:
        result = dumps([])
    else:
        station_query = StationAutocomplete.query.filter_by(input=name)
        station_exists = db.session.query(station_query.exists()).scalar()

        if station_exists:
            result = station_query.first().result
        else:
            access_token = get_valid_access_token()
            if not access_token:
                result = dumps([])
            else:
                result = dumps(get_station_names(name, access_token=access_token))
                db.session.add(StationAutocomplete(input=name, result=result))
                db.session.commit()

    return Response(result, mimetype='application/json')


@ticket_price.route("/journeys", methods=['GET', 'POST'])
@auth_required()
def journeys():
    add_journey_form = JourneyForm()
    delete_journeys_form = DeleteJournalForm()

    if add_journey_form.submit.data and add_journey_form.validate():
        journey = Journey(user_id=current_user.id, origin=add_journey_form.origin.data,
                          destination=add_journey_form.destination.data,
                          price=add_journey_form.price.data, date=add_journey_form.date.data)
        db.session.add(journey)
        db.session.commit()
        flash('Journal entry added.')

    if delete_journeys_form.delete.data and delete_journeys_form.validate():
        Journey.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash('All journal entries deleted.')

    journeys_list = Journey.query.filter_by(user_id=current_user.id).order_by(Journey.date.desc()).all()

    titles = [('origin', 'Origin'), ('destination', 'Destination'), ('price', 'Price in €'), ('date', 'Date')]
    journey_count = len(journeys_list)
    price_sum = round(sum(journey.price for journey in journeys_list), 2)
    klimaticket_gains = round(price_sum - current_user.klimaticket_price, 2)

    return render_template('journeys.html', add_journey_form=add_journey_form,
                           delete_journeys_form=delete_journeys_form, table=journeys_list, titles=titles,
                           journey_count=journey_count,
                           price_sum=price_sum, klimaticket_gains=klimaticket_gains)


@ticket_price.route('/export_journeys')
@auth_required()
def export_journeys():
    def generate():
        data = StringIO()
        w = csv.writer(data)
        w.writerow(('Origin', 'Destination', 'Price in €', 'Date'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        journeys_list = Journey.query.filter_by(user_id=current_user.id).all()
        for journey in journeys_list:
            w.writerow((journey.origin, journey.destination, journey.price, journey.date))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    response = Response(stream_with_context(generate()), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="exported_journeys.csv")
    return response


# TODO: whole view mostly temporary
@ticket_price.route('/sse_container', methods=['POST'])
@auth_required()
def sse_container():
    # TODO: do not use the price form!
    form = PriceForm()
    print(form.vorteilscard.data)
    form.vorteilscard.data = current_user.has_vorteilscard
    print(form.vorteilscard.data)
    print(current_user.has_vorteilscard)

    return render_template('sse_container.html', form=form, output_only_price=True)


@ticket_price.route("/profile", methods=['GET', 'POST'])
@auth_required()
def profile():
    form = ProfileForm()

    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).one()
        user.has_vorteilscard = form.has_vorteilscard.data
        user.klimaticket_price = form.klimaticket_price.data
        db.session.commit()
    else:
        form.has_vorteilscard.data = current_user.has_vorteilscard
        form.klimaticket_price.data = current_user.klimaticket_price

    return render_template('profile.html', form=form, name=current_user.email)
