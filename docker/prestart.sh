#!/bin/sh

pybabel compile -d app/translations

if flask is-db-init; then
    echo "Running database upgrade."
    flask db upgrade 
else
    echo "Initizalizing database."
    flask init-db
    flask db stamp head
fi
