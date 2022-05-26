from flask import render_template, Blueprint, Response, stream_with_context

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
    return Response(stream_with_context(get_price_generator(origin, destination)), mimetype='text/event-stream')


# TODO: split?
def get_price_generator(origin, destination, date=None, has_vc66=False, access_token=None):
    price_query = Price.query.filter_by(origin=origin, destination=destination)
    price_exists = db.session.query(price_query.exists()).scalar()
    total_steps = 8
    current_step = 0

    def render(message, step=None):
        if step:
            progress = int(step / total_steps * 100)
        else:
            progress = None
        output = {'progress': progress, 'message': message}
        return render_template('sse_message.txt', **output)

    current_step += 1
    yield render('Checking local cache', current_step)

    if price_exists:
        price = price_query.first().price
        message = f'Price for a ticket from {origin} to {destination}: <b>{price} €</b>'
        yield render(message)
        return

    current_step += 1
    if not access_token:
        message = 'Generating access token'
        render(message, current_step)
        access_token = get_access_token()

        if not access_token:
            message = 'Failed to generate access token'
            yield render(message)
            return

    current_step += 1
    message = 'Processing origin'
    yield render(message, current_step)
    origin_id = get_station_id(origin, access_token=access_token)
    if not origin_id:
        message = 'Failed to process origin'
        yield render(message)
        return

    current_step += 1
    message = 'Processing destination'
    yield render(message, current_step)
    destination_id = get_station_id(destination, access_token=access_token)
    if not destination_id:
        message = 'Failed to process destination'
        yield render(message)
        return

    current_step += 1
    message = 'Processing travel action'
    yield render(message, current_step)
    travel_action_id = get_travel_action_id(origin_id, destination_id, date=date, access_token=access_token)
    if not travel_action_id:
        message = 'Failed to process travel action'
        yield render(message)
        return

    current_step += 1
    message = 'Processing connection'
    yield render(message, current_step)
    connection_id = get_connection_id(travel_action_id, date=date, has_vc66=has_vc66, access_token=access_token)
    if not connection_id:
        message = 'Failed to process connection'
        yield render(message)
        return

    current_step += 1
    message = 'Retrieving price'
    yield render(message, current_step)
    price = get_price_for_connection(connection_id, access_token=access_token)
    if not price:
        message = 'Failed to retrieve price'
        yield render(message)
        return

    db.session.add(Price(origin=origin, destination=destination, price=price))
    db.session.commit()
    message = f'Price for a ticket from {origin} to {destination}: <b>{price} €</b>'
    yield render(message)
