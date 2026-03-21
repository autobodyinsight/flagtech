from functools import wraps
from threading import Lock


_schema_state_lock = Lock()
_schema_bootstrapped = False


def is_schema_bootstrapped() -> bool:
    with _schema_state_lock:
        return _schema_bootstrapped


def set_schema_bootstrapped(value: bool) -> None:
    global _schema_bootstrapped
    with _schema_state_lock:
        _schema_bootstrapped = bool(value)


def skip_if_schema_bootstrapped(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if is_schema_bootstrapped():
            return None
        return func(*args, **kwargs)

    return wrapper