from typing import NamedTuple
from datetime import date as Date

from aiopg.connection import Connection


class Review(NamedTuple):
    id: int
    date: Date
    course_id: int
    review_text: str

    @classmethod
    def from_raw(cls, raw: tuple):
        return cls(*raw) if raw else None

    @staticmethod
    async def get_for_course(conn: Connection, course_id: int):
        q = ('SELECT id, date, course_id, review_text '
             'FROM course_reviews WHERE course_id = %s '
             'ORDER BY date')
        params = (course_id,)
        async with conn.cursor() as cur:
            await cur.execute(q, params)
            result = await cur.fetchall()
            return [Review.from_raw(r) for r in result]

    @staticmethod
    async def create(conn: Connection, course_id: int,
                     review_text: str):
        q = ('INSERT INTO course_reviews (course_id, review_text) '
             'VALUES (%(course_id)s, %(review_text)s)')
        params = {'course_id': course_id,
                  'review_text': review_text}
        async with conn.cursor() as cur:
            await cur.execute(q, params)
