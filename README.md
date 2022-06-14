# oebb-ticket-price
Minimal web app to retrieve prices for train journeys from [oebb.at](https://www.oebb.at) (Austrian Federal Railways).

## Components
The application uses the following components.
1. [Flask](https://flask.palletsprojects.com) for the backend
2. [htmx](https://htmx.org/) for asynchronous HTTP requests and [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
3. [Bootstrap](https://getbootstrap.com/) for front end layout

## File Structure
The application is structured as follows.
- ```util/``` contains library functions to interact with the oebb.at web API. Could potentially be used as an individual library.
- ```templates/``` contains the Jinja2 templates used by Flask.
- ```app.py``` is the Flask application's implementation.
- ```config.py``` contains configuration parameters for the application.
- ```views.py``` contains the routes offered by the app.
- ```forms.py``` contains the input forms.

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
4. Initialize the database
   ```
   flask init-db
   ```
5. Adapt the translation
   ```bash
   pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .
   pybabel update -i messages.pot -d translations
   # Adapt translations/de/LC_MESSAGES/messages.po
   pybabel compile -d translations
   ```
6. Run the app
    ```
    export FLASK_ENV=development
    export FLASK_APP=app
    flask run
    ```
7. Open in your browser: http://localhost:5000

## Live Demo
A live version can be reached at https://zug.lol

![An animation showing the functionality](demo.gif "Demo")

## Deploy
The following files can be helpful to deploy the application:
1. `oebb-ticket-price.service` as systemd service file.
2. `wsgi.py` to start the WSGI.
3. `post-receive` as git post-receive hook to finish deployment.

To use nginx as a proxy the following config snippet can be used inside a ```server``` section.

```
location / {
   include proxy_params;
   proxy_pass http://unix:/var/www/oebb-ticket-price/oebb-ticket-price.sock;
   proxy_buffering off;
}
```
