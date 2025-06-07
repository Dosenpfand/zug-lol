from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING, Iterator

from flask import render_template, request, redirect, url_for, current_app
from flask_babel import lazy_gettext as _, format_decimal

if TYPE_CHECKING:
    from werkzeug import Response as BaseResponse

from app.db import db
from app.models import Price, AuthToken
from util.oebb import (
    get_station_details,
    get_travel_action_id,
    get_connection_ids,
    get_price_for_connection,
)


def render(
    message: str, step: Optional[int] = None, total_steps: Optional[int] = None
) -> str:
    if step and total_steps:
        progress = int(step / total_steps * 100)
    else:
        progress = None
    output = {"progress": progress, "message": message}
    return render_template("sse_message.txt", **output)


def get_price_generator(
    origin: str,
    destination: str,
    date: Optional[datetime] = None,
    has_vc66: bool = False,
    output_only_price: bool = False,
    access_token: Optional[str] = None,
) -> Iterator[str]:
    logger = current_app.logger

    if not date:
        date = (datetime.utcnow() + timedelta(days=1)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )

    price_message_template = (
        "{price}"
        if output_only_price
        else _(
            '<p>Price for a ticket from {origin} to {destination}:</p><p><mark class="display-4">{price} €</mark></p>'
        )
    )
    price_query = Price.query.filter_by(
        origin=origin, destination=destination, is_vorteilscard=has_vc66
    )
    price_exists = db.session.query(price_query.exists()).scalar()
    total_steps = 8
    current_step = 0

    current_step += 1
    yield render(_("Checking local cache"), current_step, total_steps)

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
        yield render(current_message, current_step, total_steps)
        access_token = AuthToken.get_valid_one()
        if not access_token:
            logger.warning("Could not get access token.")
            current_message = _("Failed to generate access token")
            yield render(current_message)
            return

    current_step += 1
    current_message = _("Processing origin")
    yield render(current_message, current_step, total_steps)
    origin_details = get_station_details(origin, access_token=access_token)
    if not origin_details or not origin_details.get("number"):
        logger.warning("Could not process origin.")
        current_message = _("Failed to process origin")
        yield render(current_message)
        return

    current_step += 1
    current_message = _("Processing destination")
    yield render(current_message, current_step, total_steps)
    destination_details = get_station_details(destination, access_token=access_token)
    if not destination_details or not destination_details.get("number"):
        logger.warning("Could not process destination.")
        current_message = _("Failed to process destination")
        yield render(current_message)
        return

    current_step += 1
    current_message = _("Processing travel action")
    yield render(current_message, current_step, total_steps)
    travel_action_id = get_travel_action_id(
        str(origin_details["number"]),
        str(destination_details["number"]),
        date=date,
        access_token=access_token,
    )
    if not travel_action_id:
        logger.warning("Could not process travel action.")
        current_message = _("Failed to process travel action")
        yield render(current_message)
        return

    current_step += 1
    current_message = _("Processing connections")
    yield render(current_message, current_step, total_steps)
    connection_ids = get_connection_ids(
        travel_action_id,
        origin_details,
        destination_details,
        date=date,
        get_only_first=False,
        access_token=access_token,
    )
    if not connection_ids:
        logger.warning("Could not process connections.")
        current_message = _("Failed to process connections")
        yield render(current_message)
        return

    current_step += 1
    current_message = _("Retrieving price")
    yield render(current_message, current_step, total_steps)
    price = get_price_for_connection(
        connection_ids, access_token=access_token, has_vc66=has_vc66
    )
    if not price:
        logger.warning("Could not retrieve price.")
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


def post_redirect() -> "BaseResponse":
    endpoint = request.endpoint
    if not endpoint:
        current_app.logger.error("Could not determine endpoint from request.")
        endpoint = "main.home"
    return redirect(url_for(endpoint), 303)
