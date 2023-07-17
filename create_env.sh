#!/bin/sh

printenv | sed 's/^\(.*\)$/export \1/g' | grep -E "^export FLASK_" > /root/get_env.sh
