import logging

from flask import Flask
from flask_bootstrap import Bootstrap5

bootstrap = Bootstrap5()


def create_app(config='config'):
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    logging.getLogger().setLevel(logging.WARNING)

    app = Flask(__name__)

    with app.app_context():
        app.config.from_object(config)
        app.config.from_envvar('APPLICATION_SETTINGS', silent=True)
        bootstrap.init_app(app)
        from views import ticket_price  # noqa
        app.register_blueprint(ticket_price)
    return app
