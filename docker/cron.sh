#!/bin/bash

set -eu -o pipefail

trap 'cleanup' ERR
cleanup() {
    if [ -n "${SENTRY_CRONS}" ]; then
        curl "${SENTRY_CRONS}?status=error"
    fi
}

if [ -n "${SENTRY_CRONS}" ]; then
    curl "${SENTRY_CRONS}?status=in_progress"
fi

. /root/get_env.sh
cd /app
flask update-oldest-price 10 30 >> /var/log/cron.log 2>&1

if [ -n "${SENTRY_CRONS}" ]; then
    curl "${SENTRY_CRONS}?status=ok"
fi
