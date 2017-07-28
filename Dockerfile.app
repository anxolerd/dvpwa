FROM python:alpine3.6

COPY requirements.txt /tmp

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install -r /tmp/requirements.txt \
    && apk del build-deps

RUN rm -rf /tmp/requirements.txt

WORKDIR /app
ADD ./run.py /app
ADD ./sqli /app/sqli
ADD ./config /app/config
