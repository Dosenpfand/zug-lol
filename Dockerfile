FROM tiangolo/meinheld-gunicorn:python3.9

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade wheel
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./ /app
