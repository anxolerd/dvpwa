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

To rebuild the container, please use ``./recreate.sh`` script, which will
delete old container and create new from scratch. This script is primarly used
in order to rebuild application image.

If you have screwed up the database (i.e. with ``DROP TABLE students;``, please
issue the following commands to recreate database container:

.. code-block :: bash

    docker-compose stop postgres
    docker-compose rm  # make sure, you remove only images you want to recreate
    docker-compose up postgres  # recreate container and run

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


Vulnerabilities
===============

Session fixation
----------------

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Open http://localhost:8080.
2. Open browser devtools.
3. Get value for ``AIOHTTP_SESSION`` cookie.
4. Open http://localhost:8080 in the incognito tab.
5. In the incognito tab, change cookie value to the one, obtained in step 3.
6. In the normal tab (the one from steps 1-3) log in as any user.
7. Refresh page in the incognito tab.

Result
~~~~~~

You are now logged in the incognito tab as user from step 6 as well.

Mitigation
~~~~~~~~~~

Rotate session identifiers on every single login and logout. Rotate session
identifiers on every user_id and/or permissions change.

SQL Injection
-------------

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Open http://localhost:8080.
2. Log in as ``superadmin:superadmin``.
3. Go to http://localhost:8080/students/.
4. Add new student with the name ``Robert'); DROP TABLE students CASCADE; --``.

Result
~~~~~~

Table "students" is deleted from database. You observe error message, which
says: _"relation \"students\" does not exist"_.

Mitigation
~~~~~~~~~~

Never construct database queries using string concatenation. Use
library-provided way to pass parameters and query separated. Use ORM.

Stored XSS
----------

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Open http://localhost:8080/courses/1/review.
2. Fill in review content with the following payload:

   .. code-block:: html

      <b>Is this bold?</b> Yes!

3. Submit the review by clicking "Save" button.
4. Observe the newly created review. Note that text "Is it bold?" is bold,
   which means review content is probably neither sanitized on input nor
   escaped on output.
5. Open  http://localhost:8080/courses/1/review.
6. Fill in review content with the following payload:

   .. code-block:: html
      
      <script>
        alert('I am a stored XSS. Your cookies are: ' + document.cookie);
      </script>

7. Submit the review by clicking "Save" button.
8. Observe the result.

Result
~~~~~~

Now whenever you load http://localhost:8080/courses/1, you will receive an
alert, which displays your cookie. You can play with different ways to inject
your custom javascript to the page now: event handlers (i.e. ``<img
src="nonexistent" onerror="alert(document.cookie)">``, links with javascript
targets, etc.

Mitigation
~~~~~~~~~~

Escape all untrusted content, when you output it. In this example, to mitigate
this kind of attack you can set ``autoescape=True`` when setting up templating
engine (Jinja2) in ``sqli/app.py``.
You can also sanitize text, when users input it and prohibit different kinds of
code injection.

Bad choice for storing passwords
--------------------------------

Description
~~~~~~~~~~~

As per `check_paswword function
<https://github.com/anxolerd/dvpwa/blob/master/sqli/dao/user.py#L40-L41>`_ and
`database initialization script
<https://github.com/anxolerd/dvpwa/blob/master/sqli/dao/user.py#L40-L41>`_,
passwords are not stored in the database themselves, but their md5 hashes.

Here are the problems with such approach:

- As hash function produces same output for same input, same passwords will
  produce the same hash. Passwords are vulnerable to statistical analysis: it
  is possible to determine how many people use the same password, how popular
  the password is, etc:

  .. code-block :: sql
  
     sqli=# select pwd_hash, array_agg(username), count(*)
     sqli-# from "users"
     sqli-# group by pwd_hash 
     sqli-# order by count(*) desc;
                  pwd_hash             |   array_agg    | count
     ----------------------------------+----------------+-------
      5f4dcc3b5aa765d61d8327deb882cf99 | {j.doe,s.king} |     2
      1da0bac388e8e0409a83e121e1af6ef4 | {p.parker}     |     1
      17c4520f6cfd1ab53d8745e84681eb49 | {superadmin}   |     1
     (3 rows)


- Md5 is considered quite a weak hash, thus collisions can be easily found.
  Moreover, this hash is easy to bruteforce, as well as a lot of rainbow tables
  exists for md5. For example, `CrackStation website
  <https://crackstation.net/>`_ can be used for such purposes.

Mitigation
~~~~~~~~~~

Password themselves should never be stored in database. Special hash functions
for passwords exist, such as argon2, bcrypt, pbkdf2. These functions should be
used instead of plain text passwords or weak hashes like md5, or fast hash
functions like sha1, sha2. For examples, see `password hashing
<https://pynacl.readthedocs.io/en/stable/password_hashing/>`_ section on PyNaCL
documentation.

Cross-site request forgery
--------------------------

TBA



.. _`dvwa`: http://dvwa.co.uk
.. _`bobby-tables xkcd comics`: https://xkcd.com/327/
.. _`Web vulnerabilities`: https://www.slideshare.net/OlexandrKovalchuk/web-vulnerabilities-78366279
