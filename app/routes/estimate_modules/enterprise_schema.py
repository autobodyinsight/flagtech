"""Additive schema for estimating and enterprise features.

These statements add tables and nullable columns. They do not UPDATE, DELETE,
or rewrite shop_users rows, including the architect account.
"""

from __future__ import annotations

import uuid


def ensure_enterprise_schema(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS organizations (
            id SERIAL PRIMARY KEY,
            organization_id UUID NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP
        )
        """
    )
    cur.execute("ALTER TABLE shops ADD COLUMN IF NOT EXISTS organization_id INTEGER")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shops_organization_id ON shops(organization_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_organizations_deleted_at ON organizations(deleted_at)")

    cur.execute(
        """
        SELECT id, COALESCE(NULLIF(name, ''), domain, 'Shop') AS label
        FROM shops
        WHERE organization_id IS NULL
        """
    )
    for row in cur.fetchall() or []:
        shop_pk = int(row.get("id") or 0)
        if shop_pk <= 0:
            continue
        cur.execute(
            """
            INSERT INTO organizations (organization_id, name)
            VALUES (%s::uuid, %s)
            RETURNING id
            """,
            (str(uuid.uuid4()), str(row.get("label") or "Shop")[:255]),
        )
        created = cur.fetchone() or {}
        org_id = int(created.get("id") or 0)
        if org_id:
            cur.execute(
                "UPDATE shops SET organization_id = %s WHERE id = %s AND organization_id IS NULL",
                (org_id, shop_pk),
            )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS shop_labor_rates (
            id SERIAL PRIMARY KEY,
            domain VARCHAR(255) NOT NULL UNIQUE,
            shop_id INTEGER,
            shop_uuid UUID,
            body_rate_cents INTEGER NOT NULL DEFAULT 0,
            refinish_rate_cents INTEGER NOT NULL DEFAULT 0,
            mechanical_rate_cents INTEGER NOT NULL DEFAULT 0,
            frame_rate_cents INTEGER NOT NULL DEFAULT 0,
            paint_materials_per_hour_cents INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shop_labor_rates_shop_uuid ON shop_labor_rates(shop_uuid)")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS native_estimates (
            id SERIAL PRIMARY KEY,
            public_id UUID NOT NULL UNIQUE,
            domain VARCHAR(255) NOT NULL,
            shop_id INTEGER,
            shop_uuid UUID,
            organization_id INTEGER,
            estimate_number INTEGER,
            version INTEGER NOT NULL DEFAULT 1,
            supplement_number INTEGER NOT NULL DEFAULT 0,
            parent_public_id UUID,
            status VARCHAR(32) NOT NULL DEFAULT 'draft',
            ro VARCHAR(255),
            customer JSONB NOT NULL DEFAULT '{}'::jsonb,
            vehicle JSONB NOT NULL DEFAULT '{}'::jsonb,
            vin VARCHAR(32),
            lines JSONB NOT NULL DEFAULT '[]'::jsonb,
            totals JSONB NOT NULL DEFAULT '{}'::jsonb,
            rates JSONB NOT NULL DEFAULT '{}'::jsonb,
            notes JSONB NOT NULL DEFAULT '[]'::jsonb,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_native_estimates_domain_vin ON native_estimates(domain, vin)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_native_estimates_shop_status ON native_estimates(shop_uuid, status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_native_estimates_ro ON native_estimates(domain, ro)")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id BIGSERIAL PRIMARY KEY,
            domain VARCHAR(255),
            shop_id INTEGER,
            actor_user_id INTEGER,
            actor_email VARCHAR(255),
            action VARCHAR(64) NOT NULL,
            entity_type VARCHAR(64) NOT NULL,
            entity_id VARCHAR(128),
            before_data JSONB,
            after_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id, created_at DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_domain_created ON audit_log(domain, created_at DESC)")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token_hash VARCHAR(128) NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_hash ON password_reset_tokens(token_hash)")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_mfa (
            user_id INTEGER PRIMARY KEY,
            enabled BOOLEAN NOT NULL DEFAULT FALSE,
            totp_secret TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_estimates_domain_vin ON saved_estimates(domain, vin)")
    cur.execute("ALTER TABLE saved_estimates ADD COLUMN IF NOT EXISTS source VARCHAR(32)")
