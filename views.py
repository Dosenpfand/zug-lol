from flask import render_template, Blueprint, Response, stream_with_context, request

from forms import PriceForm
from util.auth_token import get_valid_access_token
from util.oebb import get_access_token, get_station_names
from json import dumps

from util.sse import get_price_generator

ticket_price = Blueprint('ticket_price', __name__, template_folder='templates')


@ticket_price.route('/form', methods=['GET', 'POST'])
@ticket_price.route('/', methods=['GET', 'POST'])
def price_form():
    form = PriceForm()
    if form.validate_on_submit():
        return render_template('sse_container.html', form=form)
    return render_template('form.html', form=form)


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