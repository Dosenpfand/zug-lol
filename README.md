<img src="assets/logo.svg" alt="mypy logo" height="150"/>

# zug.lol

[![CI](https://github.com/Dosenpfand/zug-lol/actions/workflows/ci.yml/badge.svg)](https://github.com/Dosenpfand/zug-lol/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Dosenpfand/zug-lol/branch/master/graph/badge.svg?token=EOOLP8JKRH)](https://codecov.io/gh/Dosenpfand/zug-lol)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![mypy: checked](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)

A web application that can retrieves prices for train journeys within Austria (via [oebb.at](https://www.oebb.at))
and allows you to create a travel journal to determine if a [Klimaticket](https://www.klimaticket.at/) pays off.

## Components

The application uses the following components.

1. [Flask](https://flask.palletsprojects.com) for the backend
2. [htmx](https://htmx.org/) for asynchronous HTTP requests
   and [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
3. [Bootstrap](https://getbootstrap.com/) for front end layout

## Run

To run the application locally you can use docker-compose:
```
docker-compose up -f docker/docker-compose.yml --build -d
```
You should now be able to browse the app at http://localhost:5000 .
If you want to restore an existing database backup, place its `.sql` in the `db_backup/` folder before running the above command.
Please note that when using this method the database will not be persistent. FOr persistence uncomment the corresponding lines in the `docker-compose.yml` file.
For a docker-free setup follow these steps.

1. Create and activate a virtual environment
    ```
    python -m venv venv
    source venv/bin/activate
    ```
2. Install dependencies
    ```
    pip install -r requirements.txt
    ```
3. For local development install additional dependencies
   ```
   pip install -r requirements-dev.txt
   ```
   and install the pre-commit hooks
   ```
   pre-commit install
   ```
4. Setup a PostgreSQL database and configure it via
5. Adapt the config, either by changing the contents in ```config.py```, or by pointing the environment
   variable ```APPLICATION_SETTINGS``` to an alternative file, or by setting environment variables with
   the `FLASK_` prefix.
   At least the following variables need to be set/changed:
   ```
   FLASK_SECRET_KEY # should be generated by secrets.token_urlsafe()
   FLASK_SECURITY_PASSWORD_SALT # should be generated by secrets.SystemRandom().getrandbits(128)
   SQLALCHEMY_DATABASE_URI # Should point to the database configured in the previous step
   RECAPTCHA_PUBLIC_KEY
   RECAPTCHA_PRIVATE_KEY
   ```
   If Sentry error reporting should be performed `SENTRY_DSN` needs to be set.

6. Initialize the database
   ```
   flask init-db
   ```
7. Adapt the translation
   ```bash
   pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .
   pybabel update -i messages.pot -d app/translations
   # Adapt app/translations/de/LC_MESSAGES/messages.po
   pybabel compile -d app/translations
   ```
8. Upgrade the database schema:
   ```bash
   flask db migrate
   flask db upgrade
   ```
9. Run the app
    ```
    export FLASK_DEBUG=True
    export FLASK_APP=app
    flask run
    ```
10. Open in your browser: http://localhost:5000

## Live Demo

A live version can be reached at https://zug.lol
