import re
import uuid


def _quote_ident(value: str) -> str:
    identifier = str(value or "").strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier}")
    return f'"{identifier}"'


def _ensure_shops_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS shops (
            id SERIAL PRIMARY KEY,
            shop_id UUID,
            domain VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255),
            address TEXT,
            city VARCHAR(120),
            state VARCHAR(120),
            zip VARCHAR(20),
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS shop_id UUID")
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS name VARCHAR(255)")
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS address TEXT")
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS city VARCHAR(120)")
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS state VARCHAR(120)")
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS zip VARCHAR(20)")
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE")
    cur.execute("UPDATE shops SET active = TRUE WHERE active IS NULL")
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shops_domain_unique ON shops(domain)")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shops_shop_id_unique ON shops(shop_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shops_active ON shops(active)")
    cur.execute("SELECT id FROM shops WHERE shop_id IS NULL")
    for row in (cur.fetchall() or []):
        legacy_id = int((row or {}).get("id") or 0)
        if legacy_id <= 0:
            continue
        cur.execute("UPDATE shops SET shop_id = %s::uuid WHERE id = %s", (str(uuid.uuid4()), legacy_id))


def _ensure_parts_vendors_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parts_vendors (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            vendor_type VARCHAR(100),
            contact_person VARCHAR(255),
            phone VARCHAR(50),
            street VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(100),
            zip VARCHAR(20),
            domain VARCHAR(255) NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS vendor_type VARCHAR(100)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS contact_person VARCHAR(255)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS street VARCHAR(255)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS city VARCHAR(100)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS state VARCHAR(100)")
    cur.execute("ALTER TABLE parts_vendors ADD COLUMN IF NOT EXISTS zip VARCHAR(20)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_vendors_domain ON parts_vendors(domain)")


def _ensure_shop_settings_table(cur) -> None:
    _ensure_shops_table(cur)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS shop_settings (
            id SERIAL PRIMARY KEY,
            domain VARCHAR(255) NOT NULL,
            shop_id INTEGER,
            shop_uuid UUID,
            shop_name VARCHAR(255),
            address TEXT,
            city VARCHAR(120),
            state VARCHAR(120),
            zip_code VARCHAR(20),
            phone VARCHAR(64),
            email VARCHAR(255),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS shop_id INTEGER")
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS shop_uuid UUID")
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS shop_name VARCHAR(255)")
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS address TEXT")
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS city VARCHAR(120)")
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS state VARCHAR(120)")
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS zip_code VARCHAR(20)")
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS phone VARCHAR(64)")
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS email VARCHAR(255)")
    cur.execute("ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shop_settings_domain_unique ON shop_settings(domain)")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shop_settings_shop_id_unique ON shop_settings(shop_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shop_settings_shop_uuid ON shop_settings(shop_uuid)")


def _ensure_shop_users_table(cur) -> None:
    _ensure_shops_table(cur)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS shop_users (
            id SERIAL PRIMARY KEY,
            user_id UUID,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL,
            role VARCHAR(64) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            shop_id INTEGER,
            shop_uuid UUID,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS user_id UUID")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100)")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100)")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS email VARCHAR(255)")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS role VARCHAR(64)")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS shop_id INTEGER")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS shop_uuid UUID")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE")
    cur.execute("ALTER TABLE shop_users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shop_users_domain_email_unique ON shop_users(domain, email)")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shop_users_shop_id_email_unique ON shop_users(shop_id, email)")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shop_users_user_id_unique ON shop_users(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shop_users_shop_uuid_active ON shop_users(shop_uuid, active)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shop_users_domain_active ON shop_users(domain, active)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shop_users_shop_id_active ON shop_users(shop_id, active)")
    cur.execute("SELECT id FROM shop_users WHERE user_id IS NULL")
    for row in (cur.fetchall() or []):
        legacy_id = int((row or {}).get("id") or 0)
        if legacy_id <= 0:
            continue
        cur.execute("UPDATE shop_users SET user_id = %s::uuid WHERE id = %s", (str(uuid.uuid4()), legacy_id))


def _sync_shop_id_bindings(cur) -> None:
    _ensure_shops_table(cur)
    _ensure_shop_settings_table(cur)
    _ensure_shop_users_table(cur)

    cur.execute(
        """
        INSERT INTO shops (domain, name, address, city, state, zip, updated_at)
        SELECT
            ss.domain,
            NULLIF(ss.shop_name, ''),
            NULLIF(ss.address, ''),
            NULLIF(ss.city, ''),
            NULLIF(ss.state, ''),
            NULLIF(ss.zip_code, ''),
            CURRENT_TIMESTAMP
        FROM shop_settings ss
        WHERE COALESCE(ss.domain, '') <> ''
        ON CONFLICT (domain)
        DO UPDATE SET
            name = COALESCE(NULLIF(EXCLUDED.name, ''), shops.name),
            address = COALESCE(NULLIF(EXCLUDED.address, ''), shops.address),
            city = COALESCE(NULLIF(EXCLUDED.city, ''), shops.city),
            state = COALESCE(NULLIF(EXCLUDED.state, ''), shops.state),
            zip = COALESCE(NULLIF(EXCLUDED.zip, ''), shops.zip),
            updated_at = CURRENT_TIMESTAMP
        """
    )

    cur.execute(
        """
        INSERT INTO shops (domain, updated_at)
        SELECT DISTINCT su.domain, CURRENT_TIMESTAMP
        FROM shop_users su
        WHERE COALESCE(su.domain, '') <> ''
        ON CONFLICT (domain) DO NOTHING
        """
    )

    cur.execute(
        """
        UPDATE shop_settings ss
        SET shop_id = s.id
        FROM shops s
        WHERE ss.shop_id IS DISTINCT FROM s.id
          AND s.domain = ss.domain
        """
    )
    cur.execute(
        """
        UPDATE shop_users su
        SET shop_id = s.id
        FROM shops s
        WHERE su.shop_id IS DISTINCT FROM s.id
          AND s.domain = su.domain
        """
    )
    cur.execute(
        """
        UPDATE shop_settings ss
        SET shop_uuid = s.shop_id
        FROM shops s
        WHERE (ss.shop_uuid IS NULL OR ss.shop_uuid IS DISTINCT FROM s.shop_id)
          AND (
                (ss.shop_id IS NOT NULL AND s.id = ss.shop_id)
             OR (COALESCE(ss.domain, '') <> '' AND s.domain = ss.domain)
          )
        """
    )
    cur.execute(
        """
        UPDATE shop_users su
        SET shop_uuid = s.shop_id
        FROM shops s
        WHERE (su.shop_uuid IS NULL OR su.shop_uuid IS DISTINCT FROM s.shop_id)
          AND (
                (su.shop_id IS NOT NULL AND s.id = su.shop_id)
             OR (COALESCE(su.domain, '') <> '' AND s.domain = su.domain)
          )
        """
    )


def _ensure_chat_messages_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            domain VARCHAR(255) NOT NULL,
            shop_id INTEGER,
            shop_uuid UUID,
            sender_user_id INTEGER NOT NULL,
            recipient_user_id INTEGER NOT NULL,
            kind VARCHAR(24) NOT NULL DEFAULT 'message',
            body TEXT NOT NULL,
            read_at TIMESTAMP NULL,
            completed_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS shop_id INTEGER")
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS shop_uuid UUID")
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS sender_user_id INTEGER")
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS recipient_user_id INTEGER")
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS kind VARCHAR(24) NOT NULL DEFAULT 'message'")
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS body TEXT")
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS read_at TIMESTAMP NULL")
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP NULL")
    cur.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute(
        """
        UPDATE chat_messages m
        SET shop_uuid = s.shop_id
        FROM shops s
        WHERE m.shop_uuid IS NULL
          AND (
                (m.shop_id IS NOT NULL AND s.id = m.shop_id)
             OR (COALESCE(m.domain, '') <> '' AND s.domain = m.domain)
          )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_domain_pair_created ON chat_messages(domain, sender_user_id, recipient_user_id, created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_domain_recipient_unread ON chat_messages(domain, recipient_user_id, read_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_shop_uuid_created ON chat_messages(shop_uuid, sender_user_id, recipient_user_id, created_at)")


def _ensure_saved_estimates_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_estimates (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255),
            vehicle TEXT,
            year VARCHAR(10),
            make VARCHAR(50),
            model VARCHAR(50),
            owner_info TEXT,
            insurance_company TEXT,
            claim_number VARCHAR(64),
            phone_original TEXT,
            phone_override TEXT,
            customer_phones JSONB,
            customer_email TEXT,
            vin VARCHAR(32),
            labor_repairs JSONB,
            paint_repairs JSONB,
            parts_repairs JSONB,
            estimate_snapshot JSONB,
            estimate_totals JSONB,
            parts_total NUMERIC,
            grand_total NUMERIC,
            deductible NUMERIC,
            customer_pay NUMERIC,
            insurance_pay NUMERIC,
            in_date DATE DEFAULT CURRENT_DATE,
            ecd_date DATE,
            picked_up DATE,
            domain VARCHAR(255),
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS parts_repairs JSONB")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimate_snapshot JSONB")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimate_totals JSONB")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS parts_total NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS grand_total NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS deductible NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS customer_pay NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS insurance_pay NUMERIC")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS owner_info TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS insurance_company TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS claim_number VARCHAR(64)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS phone_original TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS phone_override TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS customer_phones JSONB")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS customer_email TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS written_by TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS estimator TEXT")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS vin VARCHAR(32)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS in_date DATE DEFAULT CURRENT_DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS ecd_date DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS picked_up DATE")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_estimates_ro_domain ON saved_estimates(ro, domain)")


def _ensure_ro_payment_totals_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_payment_totals (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            insurance_paid NUMERIC DEFAULT 0,
            customer_paid NUMERIC DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(domain, ro)
        )
        """
    )
    cur.execute("ALTER TABLE ro_payment_totals ADD COLUMN IF NOT EXISTS insurance_paid NUMERIC DEFAULT 0")
    cur.execute("ALTER TABLE ro_payment_totals ADD COLUMN IF NOT EXISTS customer_paid NUMERIC DEFAULT 0")
    cur.execute("ALTER TABLE ro_payment_totals ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("ALTER TABLE ro_payment_totals ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_payment_totals_domain_ro ON ro_payment_totals(domain, ro)")


def _ensure_ro_payment_entries_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_payment_entries (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            payer_type VARCHAR(32) NOT NULL,
            payment_method VARCHAR(16),
            check_number VARCHAR(64),
            created_by VARCHAR(255),
            amount NUMERIC NOT NULL,
            business_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS ro VARCHAR(255)")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS payer_type VARCHAR(32)")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS payment_method VARCHAR(16)")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS check_number VARCHAR(64)")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS created_by VARCHAR(255)")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS amount NUMERIC")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS business_date DATE")
    cur.execute("ALTER TABLE ro_payment_entries ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_payment_entries_domain_ro ON ro_payment_entries(domain, ro)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_payment_entries_domain_ro_type ON ro_payment_entries(domain, ro, payer_type)")


def _ensure_parts_orders_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parts_orders (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            vendor_id INTEGER,
            vendor_name VARCHAR(255),
            arrival_date DATE,
            ordered_lines JSONB,
            arrived_count INTEGER DEFAULT 0,
            returned_count INTEGER DEFAULT 0,
            domain VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_orders_domain ON parts_orders(domain)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_orders_ro ON parts_orders(ro)")


def _ensure_parts_received_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parts_received (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            line_id INTEGER NOT NULL,
            vendor VARCHAR(255) NOT NULL,
            description TEXT,
            part_number VARCHAR(255),
            qty_received NUMERIC,
            list_price NUMERIC,
            cost NUMERIC,
            eta DATE,
            invoice_number VARCHAR(255),
            invoice_total NUMERIC,
            returned BOOLEAN DEFAULT FALSE,
            returned_at TIMESTAMP,
            received_business_date DATE,
            returned_business_date DATE,
            domain VARCHAR(255) NOT NULL,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS description TEXT")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS part_number VARCHAR(255)")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS qty_received NUMERIC")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS list_price NUMERIC")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS eta DATE")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS invoice_number VARCHAR(255)")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS invoice_total NUMERIC")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS returned BOOLEAN DEFAULT FALSE")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS returned_at TIMESTAMP")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS received_business_date DATE")
    cur.execute("ALTER TABLE parts_received ADD COLUMN IF NOT EXISTS returned_business_date DATE")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parts_received_ro_domain ON parts_received(ro, domain)")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_parts_received_unique ON parts_received(ro, line_id, domain)")


def _ensure_ro_phases_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_phases (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            phase VARCHAR(50) NOT NULL,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_phases_ro_domain ON ro_phases(ro, domain)")


def _ensure_ro_notes_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_notes (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            note TEXT NOT NULL,
            domain VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_notes ADD COLUMN IF NOT EXISTS created_by VARCHAR(255)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_notes_ro_domain ON ro_notes(ro, domain)")


def _ensure_ro_activity_log_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_activity_log (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            activity_type VARCHAR(64) NOT NULL,
            message TEXT NOT NULL,
            occurred_on DATE NOT NULL DEFAULT CURRENT_DATE,
            domain VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ro_activity_ro_domain ON ro_activity_log(ro, domain, created_at DESC)")


def _ensure_ro_assignments_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_assignments (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            tech_id INTEGER,
            tech_name VARCHAR(255),
            excluded_lines JSONB,
            assigned_hours NUMERIC,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_assignments ADD COLUMN IF NOT EXISTS assigned_hours NUMERIC")
    cur.execute(
        """
        SELECT indexname FROM pg_indexes
        WHERE indexname = 'idx_ro_assignments_ro_role_domain'
        """
    )
    index_exists = cur.fetchone()
    if not index_exists:
        cur.execute(
            """
            DELETE FROM ro_assignments a
            WHERE id NOT IN (
                SELECT MAX(id) FROM ro_assignments
                GROUP BY ro, role, domain
            )
            """
        )
        cur.execute(
            """
            CREATE UNIQUE INDEX idx_ro_assignments_ro_role_domain
            ON ro_assignments(ro, role, domain)
            """
        )


def _ensure_ro_line_assignments_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_line_assignments (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            repair_type VARCHAR(20) NOT NULL,
            line_key VARCHAR(64) NOT NULL,
            line_number VARCHAR(64),
            description TEXT,
            hours NUMERIC,
            tech_id INTEGER,
            tech_name VARCHAR(255),
            source_repair_type VARCHAR(20),
            is_pending BOOLEAN DEFAULT FALSE,
            domain VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS is_pending BOOLEAN DEFAULT FALSE")
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS source_repair_type VARCHAR(20)")
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS ready_to_flag BOOLEAN DEFAULT FALSE")
    cur.execute("ALTER TABLE ro_line_assignments ADD COLUMN IF NOT EXISTS flagged_at TIMESTAMP")
    cur.execute(
        """
        UPDATE ro_line_assignments
        SET source_repair_type = repair_type
        WHERE source_repair_type IS NULL OR source_repair_type = ''
        """
    )
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_line_assignments_unique
        ON ro_line_assignments(ro, repair_type, line_key, domain)
        """
    )
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_line_assignments_source_unique
        ON ro_line_assignments(ro, source_repair_type, line_key, domain)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ro_line_assignments_ro_domain
        ON ro_line_assignments(ro, domain)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ro_line_assignments_ready_flag
        ON ro_line_assignments(domain, tech_id, ready_to_flag)
        """
    )


def _ensure_ro_flagout_lines_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ro_flagout_lines (
            id SERIAL PRIMARY KEY,
            ro VARCHAR(255) NOT NULL,
            tech_id INTEGER,
            tech_name VARCHAR(255),
            repair_type VARCHAR(20) NOT NULL,
            line_key VARCHAR(64) NOT NULL,
            line_number VARCHAR(64),
            description TEXT,
            hours NUMERIC,
            pay_rate NUMERIC,
            pay_amount NUMERIC,
            status VARCHAR(32) NOT NULL DEFAULT 'ready_to_flag',
            domain VARCHAR(255) NOT NULL,
            flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE ro_flagout_lines ADD COLUMN IF NOT EXISTS pay_rate NUMERIC")
    cur.execute("ALTER TABLE ro_flagout_lines ADD COLUMN IF NOT EXISTS pay_amount NUMERIC")
    cur.execute("ALTER TABLE ro_flagout_lines ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP")
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ro_flagout_lines_unique
        ON ro_flagout_lines(ro, tech_id, repair_type, line_key, domain)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ro_flagout_lines_domain_status
        ON ro_flagout_lines(domain, status, flagged_at)
        """
    )


def _ensure_techs_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS techs (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            pay_rate NUMERIC(10, 2) NOT NULL,
            domain VARCHAR(255),
            active BOOLEAN DEFAULT TRUE,
            status VARCHAR(32) DEFAULT 'Active',
            role VARCHAR(100) DEFAULT '',
            total_ros INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE")
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS status VARCHAR(32) DEFAULT 'Active'")
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS role VARCHAR(100) DEFAULT ''")
    cur.execute("ALTER TABLE techs ADD COLUMN IF NOT EXISTS total_ros INTEGER DEFAULT 0")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_techs_domain ON techs(domain)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_techs_active ON techs(active)")


def _ensure_archived_techs_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS archived_techs (
            id SERIAL PRIMARY KEY,
            tech_id INTEGER NOT NULL,
            tech_name VARCHAR(255) NOT NULL,
            pay_rate NUMERIC(10, 2),
            assigned_ros JSONB,
            total_hours NUMERIC,
            domain VARCHAR(255),
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE archived_techs ADD COLUMN IF NOT EXISTS domain VARCHAR(255)")
    cur.execute("ALTER TABLE archived_techs ADD COLUMN IF NOT EXISTS assigned_ros JSONB")
    cur.execute("ALTER TABLE archived_techs ADD COLUMN IF NOT EXISTS total_hours NUMERIC")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_archived_techs_domain_archived ON archived_techs(domain, archived_at DESC)")
