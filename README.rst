===============================================
DVPWA -- Damn Vulnerable Python Web Application
===============================================

.. image:: https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg
   :alt: StandWithUkraine
   :align: center
   :target: https://stand-with-ukraine.pp.ua

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

Note that reviews are not the only injection point. Student names, course
titles and course descriptions are also rendered without escaping. See
`Stored XSS in other fields`_ below.

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

Description
~~~~~~~~~~~

CSRF protection is effectively disabled. A token is generated and inserted
into forms (see ``sqli/utils/jinja2.py``), but the middleware that should
validate it is commented out in ``sqli/app.py``. As a result, no POST request
checks whether ``_csrf_token`` is present or valid.

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Open http://localhost:8080 and log in as ``superadmin:superadmin``.
2. Create a page on another origin (for example, ``attacker.example``) with
   the following content:

   .. code-block:: html

      <form action="http://localhost:8080/students/" method="POST" id="csrf">
        <input type="hidden" name="name" value="Student created via CSRF">
      </form>
      <script>document.getElementById('csrf').submit();</script>

3. While still logged in, open the attacker page in the same browser.
4. Open http://localhost:8080/students/ and observe the new student.

The same technique works for the other POST endpoints, because none of them
validate the token:

.. code-block:: html

   <!-- Add a mark as an administrator -->
   <form action="http://localhost:8080/students/1/evaluate/1" method="POST">
     <input type="hidden" name="points" value="5">
   </form>

   <!-- Log the victim out -->
   <form action="http://localhost:8080/logout/" method="POST"></form>

Login CSRF is also possible: an attacker can submit the login form on behalf
of the victim and authenticate them into the attacker's account.

Result
~~~~~~

State-changing requests are executed with the victim's session without the
victim's intention. In the case of ``/logout/`` the victim is logged out; in
the case of evaluation or course creation an attacker can perform actions
that the UI only shows to administrators. Login CSRF allows the attacker to
force the victim into an account controlled by the attacker.

Mitigation
~~~~~~~~~~

Enable CSRF middleware and validate the token on the server for every
state-changing request. The existing implementation can be reused, but it
must be imported and added to the middleware list in ``sqli/app.py``:

.. code-block:: python

   from sqli.middlewares import (
       session_middleware, csrf_middleware, error_middleware,
   )

   app = Application(
       middlewares=[
           session_middleware,
           csrf_middleware,
           error_middleware,
       ]
   )

Additionally, set the session cookie to ``SameSite=Lax`` or
``SameSite=Strict``, reject requests with missing or invalid tokens with
HTTP 403, and do not rely on the presence of a hidden input in HTML as
protection.

Missing authorization
---------------------

Description
~~~~~~~~~~~

Access restrictions exist only in templates: forms for adding students,
creating courses, evaluating students and writing reviews are hidden from
unauthorized users or non-administrators. However, the corresponding view
functions do not perform any authorization checks.

``sqli/utils/auth.py`` provides an ``authorize`` decorator with an
``ensure_admin`` option, but it is only applied to ``logout``. In particular,
``ensure_admin=True`` is never used anywhere in the project.

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Do not log in. All requests below are performed anonymously.
2. Add a student:

   .. code-block:: bash

      curl -X POST \
           --data-urlencode 'name=Mallory' \
           http://localhost:8080/students/

3. Create a course, although the form is only rendered for administrators:

   .. code-block:: bash

      curl -X POST \
           --data-urlencode 'title=Course created anonymously' \
           --data-urlencode 'description=No authorization required' \
           http://localhost:8080/courses/

4. Evaluate a student, although the form is only rendered for administrators:

   .. code-block:: bash

      curl -X POST \
           --data-urlencode 'points=5' \
           http://localhost:8080/students/1/evaluate/1

5. Add a review without being logged in:

   .. code-block:: bash

      curl -X POST \
           --data-urlencode 'review_text=Anonymous review' \
           http://localhost:8080/courses/1/review

Result
~~~~~~

An unauthenticated user can create students, courses, marks and reviews. A
regular authenticated user can perform administrator-only actions, such as
creating courses and evaluating students. Hiding controls in templates
provides no protection.

Mitigation
~~~~~~~~~~

Enforce authorization on the server side in the view handlers:

.. code-block:: python

   @authorize()
   @template('students.jinja2')
   async def students(request: Request):
       ...

   @authorize(ensure_admin=True)
   @template('courses.jinja2')
   async def courses(request: Request):
       ...

   @authorize(ensure_admin=True)
   @template('evaluate.jinja2')
   async def evaluate(request: Request):
       ...

Apply authorization to every state-changing endpoint separately from the
GET handlers where appropriate, and add tests that call these endpoints
without a session and with a non-admin session.

Insecure session cookie
-----------------------

Description
~~~~~~~~~~~

Session storage is configured with ``httponly=False`` in
``sqli/middlewares.py``:

.. code-block:: python

   storage = RedisStorage(app['redis'], httponly=False)

The session cookie is therefore accessible from JavaScript. In addition, the
code does not set the ``Secure`` and ``SameSite`` attributes.

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Log in at http://localhost:8080 as any user.
2. Open browser developer tools and inspect the ``AIOHTTP_SESSION`` cookie.
3. Note that the ``HttpOnly`` flag is absent.
4. Run the following in the browser console:

   .. code-block:: javascript

      document.cookie

5. The session identifier is displayed, even though it is an authentication
   cookie. The response headers can also be inspected with:

   .. code-block:: bash

      curl -i -X POST \
           --data-urlencode 'username=superadmin' \
           --data-urlencode 'password=superadmin' \
           http://localhost:8080/

Result
~~~~~~

Any JavaScript running on the page, including stored XSS from the review,
student or course fields, can read the session cookie and send it to an
attacker. The cookie is also sent over plain HTTP, so it can be intercepted
on the network. The missing ``SameSite`` attribute makes cross-site requests
more likely to carry the session.

Mitigation
~~~~~~~~~~

Set secure attributes for the session cookie:

.. code-block:: python

   storage = RedisStorage(
       app['redis'],
       httponly=True,
       secure=True,
       samesite='Lax',
   )

Serve the application over HTTPS, rotate the session identifier on login and
logout, and set a reasonable ``max_age``. If possible, use a ``__Host-``
cookie prefix.

Information disclosure
----------------------

Description
~~~~~~~~~~~

The application is started with ``debug=True`` in ``sqli/app.py``. In this
mode aiohttp includes a full Python traceback in HTTP 500 responses. In
addition, the 5xx error template renders the internal dictionary of the
exception:

.. code-block:: html

   <pre>{{ error.__dict__ }}</pre>

See ``sqli/templates/errors/50x.jinja2``.

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Trigger an unhandled server error, for example by sending a POST request
   without the required ``name`` field:

   .. code-block:: bash

      curl -i -X POST \
           -H 'Accept: text/html' \
           http://localhost:8080/students/

2. Observe the HTTP 500 response. With ``debug=True`` it contains a traceback
   with file paths, source code fragments, library versions and the exception
   message.
3. If an HTTP 5xx exception reaches ``error_middleware``, open the rendered
   error page. It additionally dumps ``error.__dict__``, including fields such
   as status, reason, headers and internal text.

Result
~~~~~~

An attacker obtains information about the application internals: absolute
file paths, source code lines, framework versions, database errors and
implementation details. This information simplifies further attacks.

Mitigation
~~~~~~~~~~

Disable debug mode in any shared or production environment:

.. code-block:: python

   app = Application(debug=False, middlewares=[...])

Render a generic error page that does not include tracebacks or
``error.__dict__``. Log detailed error information on the server side only.
Never expose stack traces, SQL errors or configuration values to clients.

Stored XSS in other fields
--------------------------

Description
~~~~~~~~~~~

The Stored XSS section above describes reviews. However, reviews are not the
only injection point. Templating is configured with ``autoescape=False`` in
``sqli/app.py``, and several other user-controlled fields are rendered without
escaping:

- ``sqli/templates/students.jinja2`` -- student name;
- ``sqli/templates/courses.jinja2`` -- course title and description;
- ``sqli/templates/course.jinja2`` -- course title, description and review
  text;
- ``sqli/templates/evaluate.jinja2`` -- student name;
- ``sqli/templates/review.jinja2`` -- course title.

Because creating students and courses is also possible without authorization,
this XSS can be injected anonymously.

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Add a student with the following name:

   .. code-block:: bash

      curl -X POST \
           --data-urlencode 'name=<script>alert(document.cookie)</script>' \
           http://localhost:8080/students/

2. Open http://localhost:8080/students/ and observe the alert.
3. Create a course with the following title:

   .. code-block:: bash

      curl -X POST \
           --data-urlencode 'title=<img src=x onerror=alert(document.cookie)>' \
           --data-urlencode 'description=XSS in course description' \
           http://localhost:8080/courses/

4. Open http://localhost:8080/courses/ and observe the alert.

Result
~~~~~~

The injected JavaScript executes in the browser of every user who opens the
affected page. Combined with the missing ``HttpOnly`` flag on the session
cookie, the script can read and exfiltrate the session identifier.

Mitigation
~~~~~~~~~~

Enable autoescaping for Jinja2:

.. code-block:: python

   setup_jinja(
       app,
       loader=PackageLoader('sqli', 'templates'),
       context_processors=[csrf_processor, auth_user_processor],
       autoescape=True,
   )

Alternatively, escape every user-controlled value explicitly with ``| e``.
Validate and sanitize input on the server side, and add a Content Security
Policy that forbids inline scripts.

Missing input validation
------------------------

Description
~~~~~~~~~~~

The project defines validation schemas in ``sqli/schema/forms.py``, but only
``EVALUATE_SCHEMA`` is used. ``STUDENT_SCHEMA``, ``REVIEW_SCHEMA`` and
``COURSE_SCHEMA`` are never applied. The views read form values directly from
``request.post()``, for example:

.. code-block:: python

   await Student.create(conn, data['name'])
   await Course.create(conn, data['title'], data['description'])
   review_text = data.get('review_text')

This causes missing validation, empty values, unexpected 500 errors and feeds
the SQL injection and XSS vulnerabilities described above.

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Create a student with an empty name, although ``STUDENT_SCHEMA`` requires a
   non-empty string:

   .. code-block:: bash

      curl -X POST --data-urlencode 'name=' http://localhost:8080/students/

2. Send a request without the required field:

   .. code-block:: bash

      curl -i -X POST http://localhost:8080/students/

   The absence of the ``name`` key raises ``KeyError`` and produces HTTP 500.

3. Submit an excessively large value:

   .. code-block:: bash

      curl -X POST \
           --data-urlencode "name=$(python -c 'print("A" * 1000000)')" \
           http://localhost:8080/students/

   The value is stored and rendered on the page without an application-level
   length limit.

4. Submit a review consisting only of whitespace. The current check in
   ``sqli/views.py`` accepts it as non-empty.

Result
~~~~~~

Invalid, empty and arbitrarily large data is stored in the database.
Malformed requests produce internal server errors, and the lack of validation
makes exploitation of SQL injection and XSS easier.

Mitigation
~~~~~~~~~~

Use the existing schemas with ``check_and_return`` and return HTTP 400 with
validation errors when input is invalid:

.. code-block:: python

   try:
       data = STUDENT_SCHEMA.check_and_return(await request.post())
   except DataError as e:
       raise HTTPBadRequest(text=str(e))

Apply ``REVIEW_SCHEMA`` and ``COURSE_SCHEMA`` in the same way. Enforce maximum
lengths both in the schemas and in the database, handle missing fields
explicitly, and trim whitespace before validating required text.

Password brute force
--------------------

Description
~~~~~~~~~~~

The login handler in ``sqli/views.py`` has no rate limiting, account lockout,
delay or CAPTCHA. Usernames are predictable and are present in the fixtures,
and passwords are stored as unsalted MD5 hashes, so an attacker can try an
unlimited number of passwords.

Steps to reproduce
~~~~~~~~~~~~~~~~~~

1. Prepare a short password list, for example:

   .. code-block:: text

      password
      qwerty
      superadmin
      123456

2. Send repeated login attempts for the known ``superadmin`` user:

   .. code-block:: bash

      while read -r password; do
        curl -s -o /dev/null -w '%{http_code}\n' \
             -X POST \
             --data-urlencode 'username=superadmin' \
             --data-urlencode "password=$password" \
             http://localhost:8080/
      done < passwords.txt

3. Observe that every attempt is processed and no lockout or delay is applied.

Result
~~~~~~

An attacker can perform online brute-force or credential-stuffing attacks
against any known account. The weak password hashing makes any recovered hash
easy to crack offline as well.

Mitigation
~~~~~~~~~~

Add rate limiting per IP address and per account, exponential backoff or
temporary lockout after repeated failures, and log failed authentication
attempts. Consider CAPTCHA or multi-factor authentication for administrator
accounts. Use a slow password hashing function such as Argon2, bcrypt or
PBKDF2 instead of MD5, and return the same generic error message for unknown
usernames and wrong passwords.



.. _`dvwa`: http://dvwa.co.uk
.. _`bobby-tables xkcd comics`: https://xkcd.com/327/
.. _`Web vulnerabilities`: https://www.slideshare.net/OlexandrKovalchuk/web-vulnerabilities-78366279
