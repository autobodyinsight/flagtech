from datetime import date, datetime, timezone
import json


def _to_local_business_date(value) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if not isinstance(value, datetime):
        return None
    local_tz = datetime.now().astimezone().tzinfo or timezone.utc
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(local_tz).date()


def _parse_json_field(value):
    if value is None:
        return []
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return []


def _parse_float_value(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except Exception:
        return 0.0
