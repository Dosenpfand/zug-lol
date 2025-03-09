#!/bin/bash

set -eu -o pipefail
. /root/get_env.sh

trap 'cleanup' ERR INT TERM
cleanup() {
    if [ -n "${SENTRY_CRONS:-}" ]; then
        curl "${SENTRY_CRONS}?status=error"
    fi
}

if [ -n "${SENTRY_CRONS:-}" ]; then
    curl "${SENTRY_CRONS}?status=in_progress"
fi

cd /app
flask update-oldest-price 10 30 >> /var/log/cron.log 2>&1

if [ -n "${SENTRY_CRONS:-}" ]; then
    curl "${SENTRY_CRONS}?status=ok"
fi

trap - ERR INT TERM
