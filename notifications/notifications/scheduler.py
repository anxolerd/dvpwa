from priority import PriorityTree

DEFAULT_WEIGHT = 16


class NotificationScheduler:
    def __init__(self):
        self.tree = PriorityTree()

    def schedule(self, notification_id, depends_on=None, weight=DEFAULT_WEIGHT):
        self.tree.insert_stream(notification_id, depends_on=depends_on, weight=weight)

    def next_notification(self):
        return next(self.tree)
