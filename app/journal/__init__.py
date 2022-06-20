from flask import Blueprint

bp = Blueprint('journal', __name__, template_folder='templates')

from app.journal import views # noqa