from flask import render_template, Blueprint, Response, stream_with_context

import app
from app import db
from forms import PriceForm
from models import Price
from util.oebb import get_access_token, get_station_id, get_travel_action_id, get_connection_id, \
    get_price_for_connection

ticket_price = Blueprint('ticket_price', __name__, template_folder='templates')


@ticket_price.route('/form', methods=['GET', 'POST'])
@ticket_price.route('/', methods=['GET', 'POST'])
def price_form():
    form = PriceForm()
    if form.validate_on_submit():
        return render_template('sse_container.html', form=form)
    return render_template('form.html', form=form)


@ticket_price.route('/get_price/<string:origin>/<string:destination>')
def get_price(origin, destination):
    return Response(
        stream_with_context(get_price_generator(origin, destination)), mimetype='text/event-stream')


# TODO: move?
def get_price_generator(origin, destination, date=None, has_vc66=False, access_token=None):
    price_query = Price.query.filter_by(origin=origin, destination=destination)
    price_exists = db.session.query(price_query.exists()).scalar()

    yield 'event: UpdateEvent\ndata: Checking local cache\n\n'
    if price_exists:
        price = price_query.first().price
        yield f'event: UpdateEvent\ndata: Price for a ticket from {origin} to {destination}: <b>{price} €</b>\n\n'
        return

    if not access_token:
        yield 'event: UpdateEvent\ndata: Generating access token\n\n'
        access_token = get_access_token()
        if not access_token:
            yield 'event: UpdateEvent\ndata: Failed to generate access token\n\n'
            return

    yield 'event: UpdateEvent\ndata: Processing origin\n\n'
    origin_id = get_station_id(origin, access_token=access_token)
    if not origin_id:
        yield 'event: UpdateEvent\ndata: Failed to process origin\n\n'
        return

    yield 'event: UpdateEvent\ndata: Processing destination\n\n'
    destination_id = get_station_id(destination, access_token=access_token)
    if not destination_id:
        yield 'event: UpdateEvent\ndata: Failed to process destination\n\n'
        return

    yield 'event: UpdateEvent\ndata: Processing travel action\n\n'
    travel_action_id = get_travel_action_id(origin_id, destination_id, date=date, access_token=access_token)
    if not travel_action_id:
        yield 'event: UpdateEvent\ndata: Failed to process travel action\n\n'
        return

    yield 'event: UpdateEvent\ndata: Processing connection\n\n'
    connection_id = get_connection_id(travel_action_id, date=date, has_vc66=has_vc66, access_token=access_token)
    if not connection_id:
        yield 'event: UpdateEvent\ndata: Failed to process connection\n\n'
        return

    yield f'event: UpdateEvent\ndata: Retrieving price\n\n'
    price = get_price_for_connection(connection_id, access_token=access_token)
    if not price:
        yield 'event: UpdateEvent\ndata: Failed to retrieve price\n\n'
        return

    db.session.add(Price(origin=origin, destination=destination, price=price))
    db.session.commit()
    yield f'event: UpdateEvent\ndata: Price for a ticket from {origin} to {destination}: <b>{price} €</b>\n\n'
