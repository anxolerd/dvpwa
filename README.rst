===============================================
DVPWA -- Damn Vulnerable Python Web Application
===============================================

Description
===========

DVPWA was inspired by famous `dvwa`_ project and `bobby-tables xkcd comics`_.
The purpose of this project is to implement real-world like application in
Python with as many vulnerabilities as possible while having a good design and
intentions.

This project was used as demonstration of vulnerabilities during my 
`Web vulnerabilities`_ presentation at EVO Summer Python Lab'17.

Running
=======

Docker-compose
--------------

DVPWA is packaged into docker container. All the dependencies described in
:code:`docker-compose.yml`. You can easiliy run it and its dependencies 
using a simple command:

.. code-block :: bash

    docker-compose up

Then visit http://localhost:8080 in your favorite browser.

Natively
--------

If for some reasons you cannot use docker or docker-compose you can run the
application on your host system.

Requirements
~~~~~~~~~~~~

- Python3.6.2
- PostgreSQL database for data storage
- Redis for session storage

Installing and running
~~~~~~~~~~~~~~~~~~~~~~

.. code-block :: bash

    # Install application dependencies.
    pip install -r requirements.txt

    # Set up postgresql database Further I assume your db user
    # is named postgres and database name is sqli

    # Create database schema by applying migration 000
    psql -U postgres --d sqli --host localhot --port 5432 \
         -f migrations/000-init-schema.sql

    # Load fixtures into database
    psql -U postgres --d sqli --host localhot --port 5432 \
         -f migrations/001-fixtures.sql

    # Modify config/dev.yaml
    cat config/dev.yaml <<EOF
    db:
      user: postgres
      password: postgres
      host: localhost
      port: 5432
      database: sqli

    redis:
      host: localhost
      port: 6379
      db: 0

    app:
      host: 0.0.0.0
      port: 8080
    EOF

    # Run application
    python run.py

Then visit http://localhost:8080 in your favorite browser.

.. _`dvwa`: http://dvwa.co.uk
.. _`bobby-tables xkcd comics`: https://xkcd.com/327/
.. _`Web vulnerabilities`: https://www.slideshare.net/OlexandrKovalchuk/web-vulnerabilities-78366279
