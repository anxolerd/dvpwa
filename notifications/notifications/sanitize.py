import bleach
from bleach.sanitizer import BleachSanitizerFilter, Cleaner

ALLOWED_TAGS = ['b', 'i', 'a', 'p']


def clean_message(text):
    return bleach.clean(text, tags=ALLOWED_TAGS, strip=True)


def clean_with_cleaner(text):
    return Cleaner(tags=ALLOWED_TAGS).clean(text)


def sanitize_text_token(text):
    sanitizer = BleachSanitizerFilter(source=[], allowed_elements=ALLOWED_TAGS)
    return sanitizer.sanitize_characters({'type': 'Characters', 'data': text})
