from flask import render_template, Blueprint, Response

from forms import PriceForm
from util.oebb import get_price_generator

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
    def generate():
        for row in get_price_generator(origin, destination):
            yield row

    return Response(generate(), mimetype='text/event-stream')
