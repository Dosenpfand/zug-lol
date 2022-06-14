import logging

import click
from flask import Flask, current_app, request, session, flash
from flask.cli import with_appcontext
from flask_bootstrap import Bootstrap4
from flask_security import SQLAlchemyUserDatastore, Security
from flask_security.models import fsqla_v2 as fsqla
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel, format_number
from flask_babel import lazy_gettext as _
from flask_wtf.csrf import CSRFProtect

from forms_security import ExtendedRegisterForm

bootstrap = Bootstrap4()
db = SQLAlchemy()
security = Security()
migrate = Migrate()
babel = Babel()
csrf = CSRFProtect()


def create_app(config='config'):
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    logging.getLogger().setLevel(logging.WARNING)

    app = Flask(__name__)

    with app.app_context():
        app.config.from_object(config)
        app.config.from_envvar('APPLICATION_SETTINGS', silent=True)
        app.config.from_prefixed_env(loads=str)
        bootstrap.init_app(app)
        db.init_app(app)
        migrate.init_app(app, db)
        babel.init_app(app)
        csrf.init_app(app)

        app.jinja_env.add_extension('jinja2.ext.i18n')
        app.jinja_env.filters['format_number'] = format_number

        app.cli.add_command(init_db_command)

        fsqla.FsModels.set_db_info(db)
        from models import User, Role  # noqa
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        security.init_app(app, user_datastore, register_form=ExtendedRegisterForm)

        from views import ticket_price  # noqa
        app.register_blueprint(ticket_price)

        @babel.localeselector
        def get_locale():
            lang = request.args.get("lang", None)
            if lang in current_app.config['LANGUAGES']:
                flash(_('Language changed'))
                session['lang'] = lang
            elif 'lang' not in session:
                lang = request.accept_languages.best_match(list(current_app.config['LANGUAGES'].keys()))
                if lang:
                    session['lang'] = lang
            return session.get('lang')
    return app


# TODO: Can/Should now be deleted?
def init_db():
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
