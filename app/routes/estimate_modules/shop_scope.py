from fastapi import Request
from app.services.middleware import get_authenticated_user, get_user_domain, get_user_shop_uuid
from app.services.schema_state import skip_if_schema_bootstrapped

from .db_schema import (
    _ensure_shops_table,
    _quote_ident,
    _sync_shop_id_bindings,
)


def _resolve_first_active_shop_domain(cur) -> str:
    cur.execute(
        """
        SELECT domain
        FROM shops
        WHERE COALESCE(active, TRUE) = TRUE
          AND COALESCE(domain, '') <> ''
        ORDER BY LOWER(COALESCE(NULLIF(name, ''), domain)), id
        LIMIT 1
        """
    )
    row = cur.fetchone() or {}
    return str(row.get("domain") or "").strip().lower()


def _resolve_effective_shop_domain(cur, preferred_domain: str, allow_fallback: bool) -> str:
    normalized = str(preferred_domain or "").strip().lower()
    if normalized:
        cur.execute("SELECT domain FROM shops WHERE domain = %s LIMIT 1", (normalized,))
        match = cur.fetchone() or {}
        resolved = str(match.get("domain") or "").strip().lower()
        if resolved:
            return resolved
    if allow_fallback:
        return _resolve_first_active_shop_domain(cur)
    return normalized


@skip_if_schema_bootstrapped
def _ensure_shop_id_columns_for_domain_tables(cur) -> None:
    _ensure_shops_table(cur)
    cur.execute(
        """
                SELECT DISTINCT c.table_name
                FROM information_schema.columns c
                JOIN information_schema.tables t
                    ON t.table_schema = c.table_schema
                 AND t.table_name = c.table_name
                WHERE c.table_schema = 'public'
                    AND c.column_name = 'domain'
                    AND t.table_type = 'BASE TABLE'
        """
    )
    table_rows = cur.fetchall() or []
    for row in table_rows:
        table_name = str(row.get("table_name") or "").strip()
        if not table_name:
            continue
        if table_name == "shops":
            continue
        quoted_table = _quote_ident(table_name)
        cur.execute(f"ALTER TABLE {quoted_table} ADD COLUMN IF NOT EXISTS shop_id INTEGER")
        cur.execute(f"ALTER TABLE {quoted_table} ADD COLUMN IF NOT EXISTS shop_uuid UUID")
        cur.execute(
            f"""
            UPDATE {quoted_table} t
            SET shop_id = s.id
            FROM shops s
            WHERE t.shop_id IS NULL
              AND COALESCE(t.domain, '') <> ''
              AND s.domain = t.domain
            """
        )
        cur.execute(
            f"""
            UPDATE {quoted_table} t
            SET shop_uuid = s.shop_id
            FROM shops s
            WHERE t.shop_uuid IS NULL
              AND (
                    (t.shop_id IS NOT NULL AND s.id = t.shop_id)
                 OR (COALESCE(t.domain, '') <> '' AND s.domain = t.domain)
              )
            """
        )
        quoted_index = _quote_ident(f"idx_{table_name}_shop_id")
        cur.execute(f"CREATE INDEX IF NOT EXISTS {quoted_index} ON {quoted_table}(shop_id)")
        quoted_uuid_index = _quote_ident(f"idx_{table_name}_shop_uuid")
        cur.execute(f"CREATE INDEX IF NOT EXISTS {quoted_uuid_index} ON {quoted_table}(shop_uuid)")


@skip_if_schema_bootstrapped
def _ensure_shop_id_sync_triggers(cur) -> None:
    _ensure_shops_table(cur)
    cur.execute(
        """
        CREATE OR REPLACE FUNCTION set_shop_scope_fields()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.shop_id IS NULL AND NEW.domain IS NOT NULL THEN
                SELECT id INTO NEW.shop_id FROM shops WHERE domain = NEW.domain LIMIT 1;
            END IF;
            IF NEW.shop_uuid IS NULL AND NEW.shop_id IS NOT NULL THEN
                SELECT shop_id INTO NEW.shop_uuid FROM shops WHERE id = NEW.shop_id LIMIT 1;
            END IF;
            IF NEW.shop_id IS NULL AND NEW.shop_uuid IS NOT NULL THEN
                SELECT id INTO NEW.shop_id FROM shops WHERE shop_id = NEW.shop_uuid LIMIT 1;
            END IF;
            IF (NEW.domain IS NULL OR NEW.domain = '') AND NEW.shop_id IS NOT NULL THEN
                SELECT domain INTO NEW.domain FROM shops WHERE id = NEW.shop_id LIMIT 1;
            END IF;
            IF (NEW.domain IS NULL OR NEW.domain = '') AND NEW.shop_uuid IS NOT NULL THEN
                SELECT domain INTO NEW.domain FROM shops WHERE shop_id = NEW.shop_uuid LIMIT 1;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    cur.execute(
        """
                SELECT DISTINCT c.table_name
                FROM information_schema.columns c
                JOIN information_schema.tables t
                    ON t.table_schema = c.table_schema
                 AND t.table_name = c.table_name
                WHERE c.table_schema = 'public'
                    AND c.column_name = 'domain'
                    AND t.table_type = 'BASE TABLE'
        """
    )
    table_rows = cur.fetchall() or []
    for row in table_rows:
        table_name = str(row.get("table_name") or "").strip()
        if not table_name or table_name == "shops":
            continue
        trigger_name = f"trg_{table_name}_shop_scope"
        quoted_table = _quote_ident(table_name)
        quoted_trigger = _quote_ident(trigger_name)
        cur.execute(
            f"""
            DO $shop_scope$
            BEGIN
                CREATE TRIGGER {quoted_trigger}
                BEFORE INSERT OR UPDATE ON {quoted_table}
                FOR EACH ROW
                EXECUTE FUNCTION set_shop_scope_fields();
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END
            $shop_scope$;
            """
        )


def _resolve_request_shop_id(request: Request, cur, domain: str | None = None) -> int | None:
    auth_user = get_authenticated_user(request)
    if auth_user:
        try:
            resolved_shop_id = int(auth_user.get("shop_id") or 0)
            if resolved_shop_id:
                return resolved_shop_id
        except Exception:
            pass

    domain_value = str(domain or get_user_domain(request) or "").strip().lower()
    if not domain_value:
        return None

    cur.execute("SELECT id FROM shops WHERE domain = %s LIMIT 1", (domain_value,))
    row = cur.fetchone() or {}
    try:
        return int(row.get("id") or 0) or None
    except Exception:
        return None


def _resolve_request_shop_uuid(request: Request, cur, domain: str | None = None) -> str | None:
    auth_shop_uuid = str(get_user_shop_uuid(request) or "").strip()
    if auth_shop_uuid:
        return auth_shop_uuid

    auth_user = get_authenticated_user(request) or {}
    fallback_shop_id = int(auth_user.get("shop_id") or 0) or None
    if fallback_shop_id:
        cur.execute("SELECT shop_id FROM shops WHERE id = %s LIMIT 1", (fallback_shop_id,))
        row = cur.fetchone() or {}
        value = str(row.get("shop_id") or "").strip()
        if value:
            return value

    domain_value = str(domain or get_user_domain(request) or "").strip().lower()
    if not domain_value:
        return None
    cur.execute("SELECT shop_id FROM shops WHERE domain = %s LIMIT 1", (domain_value,))
    row = cur.fetchone() or {}
    value = str(row.get("shop_id") or "").strip()
    return value or None


@skip_if_schema_bootstrapped
def _ensure_shop_isolation_infrastructure(cur) -> None:
    _sync_shop_id_bindings(cur)
    _ensure_shop_id_columns_for_domain_tables(cur)
    _ensure_shop_id_sync_triggers(cur)
