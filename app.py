from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired

from util.oebb import get_price_generator

app = Flask(__name__)
app.config.from_object('settings')
app.config.from_envvar('APPLICATION_SETTINGS', silent=True)
bootstrap = Bootstrap5(app)


class PriceForm(FlaskForm):
    origin = StringField(label='Origin', validators=[InputRequired()], render_kw={'placeholder': 'Origin (e.g. Wien)'})
    destination = StringField(label='Destination', render_kw={'placeholder': 'Destination (e.g. Innsbruck)'},
                              validators=[InputRequired()])
    submit = SubmitField(label='Search Price')


@app.route('/form', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def price_form():
    form = PriceForm()
    if form.validate_on_submit():
        return render_template('sse_container.html', form=form)
    return render_template('form.html', form=form)


@app.route('/get_price/<string:origin>/<string:destination>')
def get_price(origin, destination):
    def generate():
        for row in get_price_generator(origin, destination):
            yield row

    return app.response_class(generate(), mimetype='text/event-stream')
