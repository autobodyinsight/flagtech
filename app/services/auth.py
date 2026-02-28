import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from app.services.db import get_conn

SESSION_COOKIE_NAME = "flagtech_session"
PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 390000
ARCHITECT_EMAIL = "jorge@autobodyinsight.com"
ALLOWED_USER_ROLES = ("user", "admin", "manager", "estimator", "tech")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def normalize_domain(value: str | None) -> str:
    return (value or "").strip().lower()


def _table_columns(table_name: str) -> set[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (table_name,),
    )
    rows = cur.fetchall() or []
    cur.close()
    return {str(r.get("column_name") or "").strip().lower() for r in rows}


def users_table_exists() -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'users'
        ) AS exists
        """
    )
    row = cur.fetchone() or {}
    cur.close()
    return bool(row.get("exists"))


def user_count() -> int:
    if not users_table_exists():
        return 0
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM users")
    row = cur.fetchone() or {}
    cur.close()
    return int(row.get("count") or 0)


def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("password is required")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    digest_b64 = base64.b64encode(digest).decode("utf-8")
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt_b64}${digest_b64}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not password or not stored_hash:
        return False

    if stored_hash.startswith(f"{PASSWORD_SCHEME}$"):
        try:
            _, iterations, salt_b64, digest_b64 = stored_hash.split("$", 3)
            salt = base64.b64decode(salt_b64)
            expected = base64.b64decode(digest_b64)
            actual = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                int(iterations),
            )
            return hmac.compare_digest(actual, expected)
        except Exception:
            return False

    return hmac.compare_digest(password, stored_hash)


def _role_column(user_columns: set[str]) -> str | None:
    if "role" in user_columns:
        return "role"
    if "access_level" in user_columns:
        return "access_level"
    return None


def _domain_column(user_columns: set[str]) -> str | None:
    if "domain" in user_columns:
        return "domain"
    return None


def _password_column(user_columns: set[str]) -> str | None:
    if "password_hash" in user_columns:
        return "password_hash"
    if "password" in user_columns:
        return "password"
    return None


def get_user_by_email(email: str) -> dict | None:
    if not users_table_exists():
        return None

    user_columns = _table_columns("users")
    role_col = _role_column(user_columns)
    password_col = _password_column(user_columns)
    domain_col = _domain_column(user_columns)

    if not password_col:
        raise RuntimeError("users table is missing password column")

    selected_role = f"{role_col} AS role" if role_col else "NULL::text AS role"
    selected_domain = f"{domain_col} AS domain" if domain_col else "NULL::text AS domain"
    selected_active = "active" if "active" in user_columns else "TRUE AS active"

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT id, email, {password_col} AS password_hash, {selected_role}, {selected_domain}, {selected_active}
        FROM users
        WHERE lower(email) = lower(%s)
        LIMIT 1
        """,
        (email,),
    )
    row = cur.fetchone()
    cur.close()
    return row


def create_user(email: str, password: str, role: str = "user") -> dict:
    if not users_table_exists():
        raise RuntimeError("users table does not exist")

    normalized_email = normalize_email(email)
    if "@" not in normalized_email:
        raise ValueError("Valid email is required")

    normalized_role = (role or "user").strip().lower()
    if normalized_role not in ALLOWED_USER_ROLES:
        raise ValueError("Invalid role")

    user_columns = _table_columns("users")
    password_col = _password_column(user_columns)
    role_col = _role_column(user_columns)
    domain_col = _domain_column(user_columns)

    if not password_col:
        raise RuntimeError("users table is missing password column")

    hashed = hash_password(password)
    domain_value = normalize_domain(normalized_email.split("@", 1)[1])

    insert_columns = ["email", password_col]
    insert_values = [normalized_email, hashed]

    if domain_col:
        insert_columns.append(domain_col)
        insert_values.append(domain_value)

    if "company_name" in user_columns:
        insert_columns.append("company_name")
        insert_values.append(domain_value)

    if role_col:
        insert_columns.append(role_col)
        insert_values.append(normalized_role)

    if "active" in user_columns:
        insert_columns.append("active")
        insert_values.append(True)

    cols_sql = ", ".join(insert_columns)
    placeholders = ", ".join(["%s"] * len(insert_columns))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE lower(email)=lower(%s)", (normalized_email,))
    if cur.fetchone():
        cur.close()
        raise ValueError("User already exists")

    cur.execute(
        f"INSERT INTO users ({cols_sql}) VALUES ({placeholders}) RETURNING id, email",
        tuple(insert_values),
    )
    created = cur.fetchone() or {}
    cur.close()
    return created


def _is_architect_session(user: dict | None) -> bool:
    if not isinstance(user, dict):
        return False
    email = normalize_email(user.get("email"))
    role = str(user.get("role") or "").strip().lower()
    return email == ARCHITECT_EMAIL or role == "architect"


def require_architect(user: dict | None) -> None:
    if not _is_architect_session(user):
        raise PermissionError("Architect access required")


def create_session_for_user(user: dict, ttl_days: int = 7) -> str:
    token = secrets.token_urlsafe(48)
    expires_at = _utc_now() + timedelta(days=ttl_days)

    session_columns = _table_columns("sessions")
    if not session_columns:
        raise RuntimeError("sessions table does not exist")

    cols = ["token"]
    vals = [token]

    if "user_id" in session_columns:
        cols.append("user_id")
        vals.append(user.get("id"))

    if "email" in session_columns:
        cols.append("email")
        vals.append(normalize_email(user.get("email")))

    if "domain" in session_columns:
        cols.append("domain")
        vals.append(user.get("domain") or normalize_domain(str(user.get("email") or "").split("@", 1)[-1]))

    if "company_name" in session_columns:
        cols.append("company_name")
        vals.append(user.get("domain") or normalize_domain(str(user.get("email") or "").split("@", 1)[-1]))

    if "access_level" in session_columns:
        cols.append("access_level")
        vals.append(user.get("role") or "user")

    if "expires_at" in session_columns:
        cols.append("expires_at")
        vals.append(expires_at)

    cols_sql = ", ".join(cols)
    placeholders = ", ".join(["%s"] * len(cols))

    conn = get_conn()
    cur = conn.cursor()
    if "expires_at" in session_columns:
        cur.execute("DELETE FROM sessions WHERE expires_at < NOW()")
    cur.execute(f"INSERT INTO sessions ({cols_sql}) VALUES ({placeholders})", tuple(vals))

    user_columns = _table_columns("users")
    if "last_login" in user_columns and user.get("id"):
        cur.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user.get("id"),))
    cur.close()
    return token


def get_session_by_token(token: str | None) -> dict | None:
    if not token:
        return None

    session_columns = _table_columns("sessions")
    if not session_columns:
        return None

    where_expires = "AND expires_at > NOW()" if "expires_at" in session_columns else ""
    role_expr = "access_level AS role" if "access_level" in session_columns else "NULL::text AS role"

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT token, user_id, email, domain, {role_expr}
        FROM sessions
        WHERE token = %s {where_expires}
        LIMIT 1
        """,
        (token,),
    )
    session = cur.fetchone()
    cur.close()
    return session


def delete_session_by_token(token: str | None) -> None:
    if not token:
        return
    if not _table_columns("sessions"):
        return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
    cur.close()


def list_users() -> list[dict]:
    if not users_table_exists():
        return []

    user_columns = _table_columns("users")
    role_col = _role_column(user_columns)
    created_expr = "created_at" if "created_at" in user_columns else "NULL::timestamp AS created_at"
    updated_expr = "updated_at" if "updated_at" in user_columns else ("created_at AS updated_at" if "created_at" in user_columns else "NULL::timestamp AS updated_at")
    role_expr = f"{role_col} AS role" if role_col else "NULL::text AS role"

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT id, email, {role_expr}, {created_expr}, {updated_expr}
        FROM users
        ORDER BY created_at ASC NULLS LAST, id ASC
        """
    )
    rows = cur.fetchall() or []
    cur.close()
    return rows


def update_user(user_id: int, email: str | None = None, role: str | None = None, password: str | None = None) -> dict | None:
    if not users_table_exists():
        return None

    user_columns = _table_columns("users")
    role_col = _role_column(user_columns)
    password_col = _password_column(user_columns)

    updates: list[str] = []
    params: list = []

    if email:
        updates.append("email = %s")
        params.append(normalize_email(email))

    if role and role_col:
        normalized_role = role.strip().lower()
        if normalized_role not in ALLOWED_USER_ROLES:
            raise ValueError("Invalid role")
        updates.append(f"{role_col} = %s")
        params.append(normalized_role)

    if password:
        if not password_col:
            raise RuntimeError("users table is missing password column")
        updates.append(f"{password_col} = %s")
        params.append(hash_password(password))

    if not updates:
        return None

    if "updated_at" in user_columns:
        updates.append("updated_at = CURRENT_TIMESTAMP")

    params.append(user_id)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING id, email",
        tuple(params),
    )
    row = cur.fetchone()
    cur.close()
    return row


def delete_user(user_id: int) -> dict | None:
    if not users_table_exists():
        return None
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s RETURNING id, email", (user_id,))
    row = cur.fetchone()
    cur.close()
    return row
