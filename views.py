from json import dumps

from flask import render_template, Blueprint, Response, stream_with_context, request
from flask_security import auth_required, current_user

from forms import PriceForm, JourneyForm, ProfileForm
from models import Journey, User
from util.auth_token import get_valid_access_token
from util.oebb import get_station_names
from util.sse import get_price_generator
from app import db

ticket_price = Blueprint('ticket_price', __name__, template_folder='templates')


@ticket_price.route('/price_form', methods=['GET', 'POST'])
@ticket_price.route('/', methods=['GET', 'POST'])
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

    return Response(stream_with_context(get_price_generator(origin, destination, has_vc66=has_vorteilscard)),
                    mimetype='text/event-stream')


@ticket_price.route('/station_autocomplete')
def station_autocomplete():
    name = request.args.get('q')
    if not name:
        result = []
    else:
        access_token = get_valid_access_token()
        if not access_token:
            result = []
        else:
            result = get_station_names(name, access_token=access_token)
    return Response(dumps(result), mimetype='application/json')


@ticket_price.route("/journeys", methods=['GET', 'POST'])
@auth_required()
def journeys():
    form = JourneyForm()
    if form.validate_on_submit():
        # TODO: support price retrieval!
        journey = Journey(user_id=current_user.id, origin=form.origin.data, destination=form.destination.data,
                          price=form.price.data)
        db.session.add(journey)
        db.session.commit()
    journeys = Journey.query.filter_by(user_id=current_user.id).all()

    titles = [('origin', 'Origin'), ('destination', 'Destination'), ('price', 'Price'), ('date', 'Date')]
    journey_count = len(journeys)
    price_sum = sum(journey.price for journey in journeys)
    klimaticket_gains = price_sum - current_user.klimaticket_price

    return render_template('journeys.html', form=form, table=journeys, titles=titles, journey_count=journey_count,
                           price_sum=price_sum, klimaticket_gains=klimaticket_gains)


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

    return render_template('profile.html', form=form)
