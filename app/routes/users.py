from fastapi import APIRouter, HTTPException, Request
from psycopg2 import sql
from psycopg2.extras import Json

from app.services.auth import ACCESS_LEVELS, ensure_auth_tables, hash_password
from app.services.db import get_conn
from app.services.middleware import get_user_domain

router = APIRouter()
ARCHITECT_EMAIL = "jorge@autobodyinsight.com"


def _ensure_architect_audit_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS architect_audit_log (
            id SERIAL PRIMARY KEY,
            actor_email VARCHAR(255) NOT NULL,
            actor_domain VARCHAR(255),
            action VARCHAR(100) NOT NULL,
            target_user_id INTEGER,
            target_email VARCHAR(255),
            target_domain VARCHAR(255),
            details JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_arch_audit_created_at ON architect_audit_log(created_at DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_arch_audit_target_domain ON architect_audit_log(target_domain)")


def _log_architect_action(
    *,
    actor_email: str,
    actor_domain: str,
    action: str,
    target_user_id: int | None = None,
    target_email: str | None = None,
    target_domain: str | None = None,
    details: dict | None = None,
) -> None:
    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    _ensure_architect_audit_table(cur)
    cur.execute(
        """
        INSERT INTO architect_audit_log (
            actor_email,
            actor_domain,
            action,
            target_user_id,
            target_email,
            target_domain,
            details
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            actor_email,
            actor_domain,
            action,
            target_user_id,
            target_email,
            target_domain,
            Json(details or {}),
        ),
    )
    cur.close()


def _session_context(request: Request) -> tuple[str, str, str]:
    domain = get_user_domain(request)
    if not domain:
        raise HTTPException(status_code=401, detail="Authentication required")

    session_user = getattr(request.state, "user", None) or {}
    session_email = str(session_user.get("email") or "").strip().lower()
    session_access_level = str(session_user.get("access_level") or "support").strip().lower()
    if session_access_level == "architect" and session_email != ARCHITECT_EMAIL:
        raise HTTPException(status_code=403, detail="Architect access is restricted")
    return domain, session_email, session_access_level


def _require_manager(session_access_level: str) -> None:
    if session_access_level != "manager":
        raise HTTPException(status_code=403, detail="Manager access required")


def _is_architect(session_email: str, session_access_level: str) -> bool:
    return session_access_level == "architect" and session_email == ARCHITECT_EMAIL


@router.get("/users")
async def list_users(request: Request):
    domain, session_email, session_access_level = _session_context(request)
    is_architect = _is_architect(session_email, session_access_level)

    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    if is_architect:
        shop_domain = str(request.query_params.get("shop_domain") or "").strip().lower()
        if shop_domain:
            cur.execute(
                """
                SELECT id, email, first_name, last_name, domain, company_name, access_level, active, created_at, last_login
                FROM users
                WHERE domain = %s
                ORDER BY domain ASC, email ASC
                """,
                (shop_domain,),
            )
        else:
            cur.execute(
                """
                SELECT id, email, first_name, last_name, domain, company_name, access_level, active, created_at, last_login
                FROM users
                ORDER BY domain ASC, email ASC
                """
            )
    elif session_access_level == "manager":
        cur.execute(
            """
            SELECT id, email, first_name, last_name, domain, company_name, access_level, active, created_at, last_login
            FROM users
            WHERE domain = %s
            ORDER BY email ASC
            """,
            (domain,),
        )
    else:
        cur.execute(
            """
            SELECT id, email, first_name, last_name, domain, company_name, access_level, active, created_at, last_login
            FROM users
            WHERE domain = %s AND lower(email) = lower(%s)
            ORDER BY email ASC
            """,
            (domain, session_email),
        )
    rows = cur.fetchall()
    cur.close()
    return {
        "users": rows,
        "domain": domain,
        "my_access_level": session_access_level,
        "can_manage_users": session_access_level == "manager" or is_architect,
        "is_architect": is_architect,
        "architect_email": ARCHITECT_EMAIL,
    }


@router.post("/users")
async def create_user(request: Request):
    domain, session_email, session_access_level = _session_context(request)
    is_architect = _is_architect(session_email, session_access_level)
    if not is_architect and session_access_level != "manager":
        raise HTTPException(status_code=403, detail="Manager access required")

    payload = await request.json()
    email = str(payload.get("email") or "").strip().lower()
    password = str(payload.get("password") or "")
    target_domain = str(payload.get("shop_domain") or domain).strip().lower() or domain
    if not is_architect and target_domain != domain:
        raise HTTPException(status_code=403, detail="Manager access required")

    company_name = str(payload.get("company_name") or target_domain).strip() or target_domain
    first_name = str(payload.get("first_name") or "").strip()
    last_name = str(payload.get("last_name") or "").strip()
    access_level = str(payload.get("access_level") or "support").strip().lower()

    if "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if access_level not in ACCESS_LEVELS:
        raise HTTPException(status_code=400, detail="Invalid access level")
    if access_level == "architect":
        raise HTTPException(status_code=400, detail="Architect access level is reserved")

    email_domain = email.split("@", 1)[1].lower()
    if email_domain != target_domain.lower():
        raise HTTPException(status_code=400, detail="User email must match your shop domain")

    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE lower(email) = lower(%s)", (email,))
    if cur.fetchone():
        cur.close()
        raise HTTPException(status_code=409, detail="User already exists")

    cur.execute(
        """
        INSERT INTO users (email, domain, company_name, first_name, last_name, password_hash, access_level, active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
        RETURNING id, email, first_name, last_name, domain, company_name, access_level, active, created_at, last_login
        """,
        (
            email,
            target_domain,
            company_name,
            first_name or None,
            last_name or None,
            hash_password(password),
            access_level,
        ),
    )
    created = cur.fetchone()
    cur.close()

    if is_architect:
        _log_architect_action(
            actor_email=session_email,
            actor_domain=domain,
            action="create_user",
            target_user_id=created.get("id"),
            target_email=created.get("email"),
            target_domain=created.get("domain"),
            details={"access_level": created.get("access_level")},
        )

    return {"ok": True, "user": created}


@router.patch("/users/{user_id}/active")
async def set_user_active(user_id: int, request: Request):
    domain, session_email, session_access_level = _session_context(request)
    is_architect = _is_architect(session_email, session_access_level)
    if not is_architect and session_access_level != "manager":
        raise HTTPException(status_code=403, detail="Manager access required")

    payload = await request.json()
    active = bool(payload.get("active"))

    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    if is_architect:
        cur.execute(
            """
            UPDATE users
            SET active = %s
            WHERE id = %s AND NOT (lower(email) = %s AND access_level = 'architect')
            RETURNING id, email, first_name, last_name, domain, company_name, access_level, active, created_at, last_login
            """,
            (active, user_id, ARCHITECT_EMAIL),
        )
    else:
        cur.execute(
            """
            UPDATE users
            SET active = %s
            WHERE id = %s AND domain = %s AND access_level <> 'architect'
            RETURNING id, email, first_name, last_name, domain, company_name, access_level, active, created_at, last_login
            """,
            (active, user_id, domain),
        )
    row = cur.fetchone()
    cur.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    if is_architect:
        _log_architect_action(
            actor_email=session_email,
            actor_domain=domain,
            action="set_user_active",
            target_user_id=row.get("id"),
            target_email=row.get("email"),
            target_domain=row.get("domain"),
            details={"active": row.get("active")},
        )

    return {"ok": True, "user": row}


@router.patch("/users/{user_id}/password")
async def reset_user_password(user_id: int, request: Request):
    domain, session_email, session_access_level = _session_context(request)
    is_architect = _is_architect(session_email, session_access_level)
    if not is_architect and session_access_level != "manager":
        raise HTTPException(status_code=403, detail="Manager access required")

    payload = await request.json()
    new_password = str(payload.get("password") or "")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    if is_architect:
        cur.execute(
            """
            UPDATE users
            SET password_hash = %s
            WHERE id = %s
            RETURNING id, email, first_name, last_name, domain, company_name, access_level, active, created_at, last_login
            """,
            (hash_password(new_password), user_id),
        )
    else:
        cur.execute(
            """
            UPDATE users
            SET password_hash = %s
            WHERE id = %s AND domain = %s AND access_level <> 'architect'
            RETURNING id, email, first_name, last_name, domain, company_name, access_level, active, created_at, last_login
            """,
            (hash_password(new_password), user_id, domain),
        )
    row = cur.fetchone()
    cur.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    if is_architect:
        _log_architect_action(
            actor_email=session_email,
            actor_domain=domain,
            action="reset_user_password",
            target_user_id=row.get("id"),
            target_email=row.get("email"),
            target_domain=row.get("domain"),
            details={},
        )

    return {"ok": True, "user": row}


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, request: Request):
    domain, session_email, session_access_level = _session_context(request)
    is_architect = _is_architect(session_email, session_access_level)
    if not is_architect:
        raise HTTPException(status_code=403, detail="Architect access required")

    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM users
        WHERE id = %s AND NOT (lower(email) = %s AND access_level = 'architect')
        RETURNING id, email, domain
        """,
        (user_id, ARCHITECT_EMAIL),
    )
    row = cur.fetchone()
    cur.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    _log_architect_action(
        actor_email=session_email,
        actor_domain=domain,
        action="delete_user",
        target_user_id=row.get("id"),
        target_email=row.get("email"),
        target_domain=row.get("domain"),
        details={},
    )

    return {"ok": True, "deleted": row}


@router.post("/shops/{shop_domain}/clear-data")
async def clear_shop_data(shop_domain: str, request: Request):
    _, session_email, session_access_level = _session_context(request)
    if not _is_architect(session_email, session_access_level):
        raise HTTPException(status_code=403, detail="Architect access required")

    domain_value = (shop_domain or "").strip().lower()
    if not domain_value:
        raise HTTPException(status_code=400, detail="Shop domain is required")

    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND column_name = 'domain'
        ORDER BY table_name
        """
    )
    tables = [r["table_name"] for r in cur.fetchall() if r["table_name"] not in {"users", "sessions"}]

    deleted_counts: dict[str, int] = {}
    for table_name in tables:
        stmt = sql.SQL("DELETE FROM {} WHERE domain = %s").format(sql.Identifier(table_name))
        cur.execute(stmt, (domain_value,))
        deleted_counts[table_name] = cur.rowcount

    cur.execute("DELETE FROM sessions WHERE domain = %s", (domain_value,))
    deleted_counts["sessions"] = cur.rowcount
    cur.close()

    _log_architect_action(
        actor_email=session_email,
        actor_domain=get_user_domain(request) or "",
        action="clear_shop_data",
        target_user_id=None,
        target_email=None,
        target_domain=domain_value,
        details={"deleted": deleted_counts},
    )

    return {
        "ok": True,
        "shop_domain": domain_value,
        "deleted": deleted_counts,
    }


@router.get("/architect/audit-logs")
async def architect_audit_logs(request: Request):
    domain, session_email, session_access_level = _session_context(request)
    if not _is_architect(session_email, session_access_level):
        raise HTTPException(status_code=403, detail="Architect access required")

    limit = request.query_params.get("limit", "100")
    shop_domain = str(request.query_params.get("shop_domain") or "").strip().lower()
    try:
        limit_value = max(1, min(500, int(limit)))
    except Exception:
        limit_value = 100

    ensure_auth_tables()
    conn = get_conn()
    cur = conn.cursor()
    _ensure_architect_audit_table(cur)

    if shop_domain:
        cur.execute(
            """
            SELECT id, actor_email, actor_domain, action, target_user_id, target_email, target_domain, details, created_at
            FROM architect_audit_log
            WHERE target_domain = %s OR actor_domain = %s
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (shop_domain, shop_domain, limit_value),
        )
    else:
        cur.execute(
            """
            SELECT id, actor_email, actor_domain, action, target_user_id, target_email, target_domain, details, created_at
            FROM architect_audit_log
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (limit_value,),
        )

    rows = cur.fetchall()
    cur.close()
    return {"logs": rows, "domain": domain, "shop_domain": shop_domain or None, "limit": limit_value}
