#!/bin/sh

. /root/get_env.sh
cd /app
flask update-oldest-price 10 30 >> /var/log/cron.log 2>&1
