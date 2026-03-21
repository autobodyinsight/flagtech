from threading import Lock

from app.routes.estimate_modules.db_schema import (
    _ensure_archived_techs_table,
    _ensure_chat_messages_table,
    _ensure_parts_orders_table,
    _ensure_parts_received_table,
    _ensure_parts_vendors_table,
    _ensure_ro_activity_log_table,
    _ensure_ro_assignments_table,
    _ensure_ro_flagout_lines_table,
    _ensure_ro_line_assignments_table,
    _ensure_ro_notes_table,
    _ensure_ro_payment_entries_table,
    _ensure_ro_payment_totals_table,
    _ensure_ro_phases_table,
    _ensure_saved_estimates_table,
    _ensure_shop_settings_table,
    _ensure_shop_users_table,
    _ensure_shops_table,
    _ensure_techs_table,
    _sync_shop_id_bindings,
)
from app.routes.estimate_modules.shop_scope import (
    _ensure_shop_id_columns_for_domain_tables,
    _ensure_shop_id_sync_triggers,
)
from app.services.db import get_conn
from app.services.schema_state import is_schema_bootstrapped, set_schema_bootstrapped


_SCHEMA_BOOTSTRAP_LOCK = Lock()
_SCHEMA_ADVISORY_LOCK_KEY_1 = 442019
_SCHEMA_ADVISORY_LOCK_KEY_2 = 903117


def _ensure_estimate_uploads_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS estimate_uploads (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            estimate_hash VARCHAR(64) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_estimate_uploads_ro_domain ON estimate_uploads(ro, domain)")


def _ensure_ro_auto_sequence(cur) -> None:
    cur.execute("CREATE SEQUENCE IF NOT EXISTS ro_auto_counter_seq START WITH 12365 MINVALUE 12365")


def initialize_application_schema() -> None:
    if is_schema_bootstrapped():
        return

    with _SCHEMA_BOOTSTRAP_LOCK:
        if is_schema_bootstrapped():
            return

        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                f"SELECT pg_advisory_lock({_SCHEMA_ADVISORY_LOCK_KEY_1}, {_SCHEMA_ADVISORY_LOCK_KEY_2})"
            )

            _ensure_shops_table(cur)
            _ensure_shop_settings_table(cur)
            _ensure_shop_users_table(cur)
            _ensure_parts_vendors_table(cur)
            _ensure_chat_messages_table(cur)
            _ensure_saved_estimates_table(cur)
            _ensure_ro_payment_totals_table(cur)
            _ensure_ro_payment_entries_table(cur)
            _ensure_parts_orders_table(cur)
            _ensure_parts_received_table(cur)
            _ensure_ro_phases_table(cur)
            _ensure_ro_notes_table(cur)
            _ensure_ro_activity_log_table(cur)
            _ensure_ro_assignments_table(cur)
            _ensure_ro_line_assignments_table(cur)
            _ensure_ro_flagout_lines_table(cur)
            _ensure_techs_table(cur)
            _ensure_archived_techs_table(cur)
            _ensure_estimate_uploads_table(cur)
            _ensure_ro_auto_sequence(cur)
            _sync_shop_id_bindings(cur)
            _ensure_shop_id_columns_for_domain_tables(cur)
            _ensure_shop_id_sync_triggers(cur)

            set_schema_bootstrapped(True)
        finally:
            try:
                cur.execute(
                    f"SELECT pg_advisory_unlock({_SCHEMA_ADVISORY_LOCK_KEY_1}, {_SCHEMA_ADVISORY_LOCK_KEY_2})"
                )
            except Exception:
                pass
            cur.close()
            conn.close()