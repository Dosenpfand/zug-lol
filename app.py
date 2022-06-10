import logging

import click
from flask import Flask
from flask.cli import with_appcontext
from flask_bootstrap import Bootstrap4
from flask_security import SQLAlchemyUserDatastore, Security
from flask_security.models import fsqla_v2 as fsqla
from flask_sqlalchemy import SQLAlchemy

bootstrap = Bootstrap4()
db = SQLAlchemy()
security = Security()


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
        app.cli.add_command(init_db_command)

        fsqla.FsModels.set_db_info(db)
        from models import User, Role  # noqa
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        security.init_app(app, user_datastore)

        from views import ticket_price  # noqa
        app.register_blueprint(ticket_price)

    return app


def init_db():
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
