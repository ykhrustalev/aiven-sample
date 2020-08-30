from datetime import timezone, datetime


def now():
    return datetime.now(timezone.utc)
