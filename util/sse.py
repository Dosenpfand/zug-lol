from flask import render_template

from app import db
from models import Price
from util.auth_token import get_valid_access_token
from util.oebb import get_access_token, get_station_id, get_travel_action_id, get_connection_id, \
    get_price_for_connection


def get_price_generator(origin, destination, date=None, has_vc66=False, access_token=None):
    price_message_template = \
        '<p>Price for a ticket from {origin} to {destination}:</p><p><mark class="display-4">{price} €</mark></p>'
    price_query = Price.query.filter_by(origin=origin, destination=destination, is_vorteilscard=has_vc66)
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
        message = price_message_template.format(origin=origin, destination=destination, price=price)
        yield render(message)
        return

    current_step += 1
    if not access_token:
        message = 'Generating access token'
        render(message, current_step)
        access_token = get_valid_access_token()

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

    db.session.add(Price(origin=origin, destination=destination, is_vorteilscard=has_vc66, price=price))
    db.session.commit()
    message = price_message_template.format(origin=origin, destination=destination, price=price)
    yield render(message)
