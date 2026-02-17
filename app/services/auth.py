import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from app.services.db import get_conn

SESSION_COOKIE_NAME = "flagtech_session"
PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 390000
ACCESS_LEVELS = ("support", "reception", "parts", "estimator", "manager", "architect")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def normalize_domain(value: str | None) -> str:
    return (value or "").strip().lower()


def normalize_shop_name(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def build_shop_scope_key(domain: str | None, company_name: str | None, email: str | None) -> str:
    normalized_domain = normalize_domain(domain)
    if normalized_domain:
        return normalized_domain

    normalized_shop_name = normalize_shop_name(company_name) or "shop"
    normalized_email = normalize_email(email)
    if normalized_email:
        return f"shop:{normalized_shop_name}|user:{normalized_email}"
    return f"shop:{normalized_shop_name}"


def ensure_auth_tables() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            domain VARCHAR(255) NOT NULL,
            company_name VARCHAR(255) NOT NULL,
            first_name VARCHAR(120),
            last_name VARCHAR(120),
            password_hash VARCHAR(255) NOT NULL,
            access_level VARCHAR(32) DEFAULT 'support',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            active BOOLEAN DEFAULT TRUE
        )
        """
    )
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS access_level VARCHAR(32) DEFAULT 'support'")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(120)")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(120)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_domain ON users(domain)")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token VARCHAR(255) PRIMARY KEY,
            user_id INTEGER,
            email VARCHAR(255),
            domain VARCHAR(255),
            company_name VARCHAR(255),
            access_level VARCHAR(32) DEFAULT 'support',
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS access_level VARCHAR(32) DEFAULT 'support'")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)")
    cur.close()


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

    # Backward-compatibility fallback for legacy plaintext hashes.
    return hmac.compare_digest(password, stored_hash)


def get_user_by_email(email: str):
    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, email, domain, company_name, password_hash, active, access_level
        FROM users
        WHERE lower(email) = lower(%s)
        LIMIT 1
        """,
        (email,),
    )
    user = cur.fetchone()
    cur.close()
    return user


def create_session_for_user(user: dict, ttl_days: int = 7) -> str:
    ensure_auth_tables()
    token = secrets.token_urlsafe(48)
    now = _utc_now()
    expires_at = now + timedelta(days=ttl_days)

    scope_key = build_shop_scope_key(
        user.get("domain"),
        user.get("company_name"),
        user.get("email"),
    )

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE expires_at < NOW()")
    cur.execute(
        """
        INSERT INTO sessions (token, user_id, email, domain, company_name, access_level, expires_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            token,
            user["id"],
            user["email"],
            scope_key,
            user["company_name"],
            user.get("access_level") or "support",
            expires_at,
        ),
    )
    cur.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user["id"],))
    cur.close()
    return token


def get_session_by_token(token: str):
    if not token:
        return None
    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT token, user_id, email, domain, company_name, access_level, expires_at
        FROM sessions
        WHERE token = %s AND expires_at > NOW()
        LIMIT 1
        """,
        (token,),
    )
    session = cur.fetchone()
    cur.close()
    return session


def delete_session_by_token(token: str) -> None:
    if not token:
        return
    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
    cur.close()


def upsert_user(
    email: str,
    password: str,
    company_name: str | None = None,
    active: bool = True,
    access_level: str = "support",
    first_name: str | None = None,
    last_name: str | None = None,
    shop_domain: str | None = None,
) -> None:
    ensure_auth_tables()
    normalized_email = normalize_email(email)
    if "@" not in normalized_email:
        raise ValueError(f"Invalid email: {email}")

    email_domain = normalized_email.split("@", 1)[1]
    user_company = company_name or email_domain
    scope_key = build_shop_scope_key(shop_domain or email_domain, user_company, normalized_email)
    normalized_first_name = (first_name or "").strip() or None
    normalized_last_name = (last_name or "").strip() or None
    password_hash = hash_password(password)
    normalized_access_level = (access_level or "support").strip().lower()
    if normalized_access_level not in ACCESS_LEVELS:
        normalized_access_level = "support"

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (email, domain, company_name, first_name, last_name, password_hash, active, access_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (email)
        DO UPDATE SET
            domain = EXCLUDED.domain,
            company_name = EXCLUDED.company_name,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            password_hash = EXCLUDED.password_hash,
            active = EXCLUDED.active,
            access_level = EXCLUDED.access_level
        """,
        (
            normalized_email,
            scope_key,
            user_company,
            normalized_first_name,
            normalized_last_name,
            password_hash,
            active,
            normalized_access_level,
        ),
    )
    cur.close()
