## build image containing the required foundation artifacts
FROM registry.access.redhat.com/ubi8/ubi:latest
USER root
WORKDIR /foundation
ENV PYTHON ${PYTHON_VERSION_UBI}

COPY requirements.txt /tmp
RUN rm -rf /tmp/requirements.txt

WORKDIR /app
ADD ./run.py /app
ADD ./sqli /app/sqli
ADD ./config /app/config
