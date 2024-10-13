FROM tiangolo/uvicorn-gunicorn:python3.11

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade wheel
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Cron job
ENV CRONTAB_FILE=/etc/cron.d/app_cron
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends cron; \
	rm -rf /var/lib/apt/lists/*
COPY docker/crontab ${CRONTAB_FILE}
COPY docker/create_env.sh /root/create_env.sh
COPY docker/cron.sh /root/cron.sh

# App
ENV MODULE_NAME=wsgi
ENV WORKER_CLASS=gthread
RUN rm -rf /app
COPY ./ /app
