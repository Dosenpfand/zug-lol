from flask import Blueprint

bp = Blueprint('ticket_price', __name__, template_folder='templates')

from app.ticket_price import views # noqa