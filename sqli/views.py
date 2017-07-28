import logging
from datetime import datetime
from itertools import groupby

from aiohttp.web import Request, HTTPFound
from aiohttp.web_exceptions import HTTPNotFound, HTTPForbidden
from aiohttp_jinja2 import template
from aiohttp_session import get_session
from trafaret import DataError

from sqli.dao.course import Course
from sqli.dao.mark import Mark
from sqli.dao.review import Review
from sqli.dao.student import Student
from sqli.dao.user import User
from sqli.schema.forms import EVALUATE_SCHEMA
from sqli.utils.auth import get_auth_user, authorize

log = logging.getLogger(__name__)


@template('index.jinja2')
async def index(request: Request):
    app: Application = request.app
    auth_user = await get_auth_user(request)

    session = await get_session(request)
    last_visited = session.get('last_visited', 'never')
    session['last_visited'] = datetime.now().isoformat()

    errors = []

    if request.method == 'POST':
        if auth_user:
            raise HTTPForbidden()
        data = await request.post()
        username = data['username']
        password = data['password']
        async with app['db'].acquire() as conn:
            user = await User.get_by_username(conn, username)
        if user and user.check_password(password):
            session['user_id'] = user.id
            auth_user = user
        else:
            errors.append('Invalid username or password')
    return {'last_visited': last_visited,
            'errors': errors,
            'auth_user': auth_user}


@template('students.jinja2')
async def students(request: Request):
    app: Application = request.app
    if request.method == 'POST':
        data = await request.post()
        async with app['db'].acquire() as conn:
            await Student.create(conn, data['name'])
    async with app['db'].acquire() as conn:
        students = await Student.get_many(conn)
    return {'students': students}


@template('student.jinja2')
async def student(request: Request):
    app: Application = request.app
    student_id = int(request.match_info['id'])
    async with app['db'].acquire() as conn:
        student = await Student.get(conn, student_id)
        if not student:
            raise HTTPNotFound()
        marks = await Mark.get_for_student(conn, student_id)
        courses = await Course.get_many(conn)
    courses_marks = {c: list(ms) for c, ms
                     in groupby(marks, lambda m: m.course_id)}
    results = [
        (course, courses_marks.get(course.id))
        for course in courses
        if course.id in courses_marks
    ]
    return {'student': student, 'results': results}


@template('courses.jinja2')
async def courses(request: Request):
    app: Application = request.app
    if request.method == 'POST':
        data = await request.post()
        async with app['db'].acquire() as conn:
            await Course.create(conn, data['title'],
                                data['description'])
    async with app['db'].acquire() as conn:
        courses = await Course.get_many(conn)
    return {'courses': courses}


@template('course.jinja2')
async def course(request: Request):
    app: Application = request.app
    course_id = int(request.match_info['id'])
    async with app['db'].acquire() as conn:
        course = await Course.get(conn, course_id)
        if not course:
            raise HTTPNotFound()
        reviews = await Review.get_for_course(conn, course_id)
        students = await Student.get_many(conn)
    return {'course': course,
            'reviews': reviews,
            'students': students}


@template('review.jinja2')
async def review(request: Request):
    app: Application = request.app
    course_id = int(request.match_info['course_id'])
    async with app['db'].acquire() as conn:
        course = await Course.get(conn, course_id)
        if not course:
            raise HTTPNotFound()
        if request.method == 'POST':
            data = await request.post()
            review_text = data.get('review_text')
            if not review_text:
                return {
                    'course': course,
                    'errors': {
                        'review_text': 'this is required field',
                    },
                }
            await Review.create(conn, course_id, review_text)
            raise HTTPFound(f'/courses/{course_id}')
        return {'course': course, 'errors': {}}


@template('evaluate.jinja2')
async def evaluate(request: Request):
    app: Application = request.app
    student_id = int(request.match_info['student_id'])
    course_id = int(request.match_info['course_id'])
    data = await request.post()
    async with app['db'].acquire() as conn:
        student = await Student.get(conn, student_id)
        course = await Course.get(conn, course_id)
        if not student or not course:
            raise HTTPNotFound()
        try:
            data = EVALUATE_SCHEMA.check_and_return(data)
        except DataError as e:
            return {'errors': e.as_dict(),
                    'course': course,
                    'student': student}
        await Mark.create(conn, student_id, course_id,
                          data['points'])
    raise HTTPFound(f'/courses/{course_id}')


@authorize()
async def logout(request: Request):
    session = await get_session(request)
    session.pop('user_id', None)
    raise HTTPFound('/')
