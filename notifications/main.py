from notifications.sanitize import clean_message, clean_with_cleaner, sanitize_text_token
from notifications.scheduler import NotificationScheduler

URGENT_WEIGHT = 256


def send_notifications(messages):
    scheduler = NotificationScheduler()
    for notification_id, _ in enumerate(messages, start=1):
        scheduler.schedule(notification_id, weight=URGENT_WEIGHT if notification_id == 1 else 16)

    first = scheduler.next_notification()
    return {
        'first': first,
        'bodies': [clean_message(message) for message in messages],
        'preview': clean_with_cleaner(messages[0]),
        'tokens': sanitize_text_token('Tom &amp; Jerry'),
    }


if __name__ == '__main__':
    print(send_notifications(['<script>alert(1)</script><b>Grades are out</b>', 'Visit <a href="/marks">marks</a>']))
