from json import dumps

from flask import render_template, request, Response, stream_with_context, redirect, url_for, flash
from flask_babel import gettext as _
from flask_login import current_user
from flask_security import auth_required

from app import db
from app.main.forms import ProfileForm, DeleteAccountForm

from app.models import User, StationAutocomplete
from app.main import bp
from util.auth_token import get_valid_access_token
from util.oebb import get_station_names
from util.sse import get_price_generator


@bp.route('/', methods=['GET'])
def home():
    return render_template('home.html', title=_('Home'))


@bp.route("/profile", methods=['GET', 'POST'])
@auth_required()
def profile():
    form = ProfileForm()

    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).one()
        user.has_vorteilscard = form.has_vorteilscard.data
        user.klimaticket_price = form.klimaticket_price.data
        db.session.commit()
    else:
        form.has_vorteilscard.data = current_user.has_vorteilscard
        form.klimaticket_price.data = current_user.klimaticket_price

    return render_template('profile.html', title=_('Profile'), form=form, name=current_user.email)


@bp.route("/delete_account", methods=['GET', 'POST'])
@auth_required()
def delete_account():
    form = DeleteAccountForm()

    if form.validate_on_submit():
        if form.is_sure.data:
            user = User.query.filter_by(id=current_user.id).first()
            db.session.delete(user)
            db.session.commit()
            flash(_('Your account has been deleted.'))
            return redirect(url_for('main.home'))

    return render_template('delete_account.html', title=_('Delete Account'), form=form)


@bp.route('/station_autocomplete')
def station_autocomplete():
    name = request.args.get('q')

    if not name:
        result = dumps([])
    else:
        station_query = StationAutocomplete.query.filter_by(input=name)
        station_exists = db.session.query(station_query.exists()).scalar()

        if station_exists:
            result = station_query.first().result
        else:
            access_token = get_valid_access_token()
            if not access_token:
                result = dumps([])
            else:
                result = dumps(get_station_names(name, access_token=access_token))
                db.session.add(StationAutocomplete(input=name, result=result))
                db.session.commit()

    return Response(result, mimetype='application/json')


@bp.route('/get_price')
def get_price():
    origin = request.args.get('origin', type=str)
    destination = request.args.get('destination', type=str)
    has_vorteilscard = request.args.get('vorteilscard', type=str, default='False') == 'True'
    output_only_price = request.args.get('output_only_price', type=bool, default='False')

    return Response(stream_with_context(
        get_price_generator(origin, destination, has_vc66=has_vorteilscard, output_only_price=output_only_price)),
        mimetype='text/event-stream')
