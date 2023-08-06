#!/bin/sh

. venv/bin/activate
./prestart.sh
export FLASK_APP=app/__init__.py
export FLASK_DEBUG=True
flask run # --debug --no-debugger
