from datetime import date, datetime


def _activity_to_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.utcnow()


def _log_ro_activity(cur, domain: str, ro: str, activity_type: str, message: str, occurred_at=None) -> None:
    if not domain or not ro or not message:
        return
    occurred_dt = _activity_to_datetime(occurred_at)
    cur.execute(
        """
        INSERT INTO ro_activity_log (ro, activity_type, message, occurred_on, domain, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (ro, activity_type, message, occurred_dt.date(), domain, occurred_dt),
    )
