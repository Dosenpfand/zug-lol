FROM tiangolo/meinheld-gunicorn:python3.9

COPY requirements.txt /tmp/requirements.txt
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install --upgrade pip
RUN pip install --upgrade wheel
RUN pip install --no-cache-dir -r /tmp/requirements.txt -r /tmp/requirements-dev.txt

# Cron job
ENV CRONTAB_FILE=/etc/cron.d/app_cron
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends cron; \
	rm -rf /var/lib/apt/lists/*
COPY docker/crontab ${CRONTAB_FILE}
COPY docker/create_env.sh /root/create_env.sh

COPY ./ /app
