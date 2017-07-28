import trafaret as T


EVALUATE_SCHEMA = T.Dict({
    T.Key('points'): T.Int(gte=0, lte=5),
})

REVIEW_SCHEMA = T.Dict({
    T.Key('review_text'): T.String(min_length=1),
})

STUDENT_SCHEMA = T.Dict({
    T.Key('name'): T.String(min_length=1),
})

COURSE_SCHEMA = T.Dict({
    T.Key('title'): T.String(min_length=1, max_length=127),
    T.Key('description', optional=True): T.String()
})
