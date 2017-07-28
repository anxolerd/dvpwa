from typing import NamedTuple

from aiopg.connection import Connection
from datetime import datetime


class Mark(NamedTuple):
    id: int
    date: datetime
    student_id: int
    course_id: int
    points: int

    @classmethod
    def from_raw(cls, raw: tuple):
        return cls(*raw) if raw else None

    @staticmethod
    async def get_for_student(conn: Connection, student_id: int):
        q = ('SELECT id, date, student_id, course_id, points '
             'FROM marks WHERE student_id = %s '
             'ORDER BY course_id, date')
        params = (student_id,)
        async with conn.cursor() as cur:
            await cur.execute(q, params)
            result = await cur.fetchall()
            return [Mark.from_raw(r) for r in result]

    @staticmethod
    async def create(conn: Connection, student_id: int,
                     course_id: int, points: int):
        q = ('INSERT INTO marks (student_id, course_id, points) '
             'VALUES (%(student_id)s, %(course_id)s, %(points)s)')
        params = {'student_id': student_id, 'course_id': course_id,
                  'points': points}
        async with conn.cursor() as cur:
            await cur.execute(q, params)
