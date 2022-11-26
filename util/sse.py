from datetime import datetime, timedelta

from flask import render_template
from flask_babel import lazy_gettext as _, format_decimal

from app import db
from app.models import Price
from util.auth_token import get_valid_access_token
from util.oebb import (
    get_station_id,
    get_travel_action_id,
    get_connection_id,
    get_price_for_connection,
)


def get_price_generator(
    origin,
    destination,
    date=None,
    has_vc66=False,
    output_only_price=False,
    access_token=None,
):
    if not date:
        date = (datetime.utcnow() + timedelta(days=1)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )

    price_message_template = (
        "{price}"
        if output_only_price
        else _(
            "<p>Price for a ticket from {origin} to {destination}:</p><p><mark"
            ' class="display-4">{price} €</mark></p>'
        )
    )
    price_query = Price.query.filter_by(
        origin=origin, destination=destination, is_vorteilscard=has_vc66
    )
    price_exists = db.session.query(price_query.exists()).scalar()
    total_steps = 8
    current_step = 0

    def render(message, step=None):
        if step:
            progress = int(step / total_steps * 100)
        else:
            progress = None
        output = {"progress": progress, "message": message}
        return render_template("sse_message.txt", **output)

    current_step += 1
    yield render(_("Checking local cache"), current_step)

    if price_exists:
        price = price_query.first().price
        current_message = price_message_template.format(
            origin=origin, destination=destination, price=format_decimal(price)
        )
        yield render(current_message)
        return

    current_step += 1
    if not access_token:
        current_message = _("Generating access token")
        render(current_message, current_step)
        access_token = get_valid_access_token()

        if not access_token:
            current_message = _("Failed to generate access token")
            yield render(current_message)
            return

    current_step += 1
    current_message = _("Processing origin")
    yield render(current_message, current_step)
    origin_id = get_station_id(origin, access_token=access_token)
    if not origin_id:
        current_message = _("Failed to process origin")
        yield render(current_message)
        return

    current_step += 1
    current_message = _("Processing destination")
    yield render(current_message, current_step)
    destination_id = get_station_id(destination, access_token=access_token)
    if not destination_id:
        current_message = _("Failed to process destination")
        yield render(current_message)
        return

    current_step += 1
    current_message = _("Processing travel action")
    yield render(current_message, current_step)
    travel_action_id = get_travel_action_id(
        origin_id, destination_id, date=date, access_token=access_token
    )
    if not travel_action_id:
        current_message = _("Failed to process travel action")
        yield render(current_message)
        return

    current_step += 1
    current_message = _("Processing connections")
    yield render(current_message, current_step)
    connection_ids = get_connection_id(
        travel_action_id,
        date=date,
        has_vc66=has_vc66,
        get_only_first=False,
        access_token=access_token,
    )
    if not connection_ids:
        current_message = _("Failed to process connections")
        yield render(current_message)
        return

    current_step += 1
    current_message = _("Retrieving price")
    yield render(current_message, current_step)
    price = get_price_for_connection(connection_ids, access_token=access_token)
    if not price:
        current_message = _("Failed to retrieve price")
        yield render(current_message)
        return

    db.session.add(
        Price(
            origin=origin,
            destination=destination,
            is_vorteilscard=has_vc66,
            price=price,
        )
    )
    db.session.commit()
    current_message = price_message_template.format(
        origin=origin, destination=destination, price=format_decimal(price)
    )
    yield render(current_message)
