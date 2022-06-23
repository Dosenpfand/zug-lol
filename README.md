# zug.lol
A web application that can retrieves prices for train journeys within Austria (via [oebb.at](https://www.oebb.at))
and allows you to create a travel journal to determine if a [Klimaticket](https://www.klimaticket.at/) pays off.

## Components
The application uses the following components.
1. [Flask](https://flask.palletsprojects.com) for the backend
2. [htmx](https://htmx.org/) for asynchronous HTTP requests and [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
3. [Bootstrap](https://getbootstrap.com/) for front end layout

## Run
To run the application locally follow these steps.

1. Create and activate a virtual environment
    ```
    python -m venv venv
    source venv/bin/activate
    ```
2. Install dependencies
    ```
    pip install -r requirements.txt
    ```
3. Adapt the config, either by changing the contents in ```config.py``` or by pointing the environment variable ```APPLICATION_SETTINGS``` to an alternative file.
   1. Setup a database and configure it via `SQLALCHEMY_DATABASE_URI`
4. Initialize the database
   ```
   flask init-db
   ```
5. Adapt the translation
   ```bash
   pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .
   pybabel update -i messages.pot -d app/translations
   # Adapt app/translations/de/LC_MESSAGES/messages.po
   pybabel compile -d app/translations
   ```
6. Upgrade the database schema:
   ```bash
   flask db upgrade
   ```
7. Run the app
    ```
    export FLASK_ENV=development
    export FLASK_APP=app
    flask run
    ```
8. Open in your browser: http://localhost:5000
9. Install pre-commit checks before committing
   ```
   pre-commit install
   ```
## Live Demo
A live version can be reached at https://zug.lol

## Deploy
The following files can be helpful to deploy the application:
1. `zug-lol.service` as systemd service file.
2. `wsgi.py` to start the WSGI.
3. `post-receive` as git post-receive hook to finish deployment.

To use nginx as a proxy the following config snippet can be used inside a ```server``` section.

```
location / {
   include proxy_params;
   proxy_pass http://unix:/var/www/zug-lol/zug-lol.sock;
   proxy_buffering off;
}
```
