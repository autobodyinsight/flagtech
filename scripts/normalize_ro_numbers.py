#!/usr/bin/env python3
"""Normalize RO values in labor_assignments and refinish_assignments."""

from __future__ import annotations

import argparse
import re

from app.services.db import get_conn


RO_PATTERN = re.compile(r"\bRO\b\s*[:#-]*\s*([A-Za-z0-9-]+)")


def normalize_ro(value: str | None) -> str:
    if value is None:
        return ""
    raw = value.strip()
    if not raw:
        return ""
    match = RO_PATTERN.search(raw)
    if match:
        return match.group(1)
    return raw


def normalize_table(cur, table: str, dry_run: bool) -> int:
    cur.execute(f"SELECT id, ro FROM {table}")
    rows = cur.fetchall()
    updated = 0

    for row in rows:
        row_id = row.get("id")
        ro = row.get("ro")
        normalized = normalize_ro(ro)
        if not normalized:
            continue
        if ro == normalized:
            continue
        updated += 1
        if not dry_run:
            cur.execute(
                f"UPDATE {table} SET ro = %s WHERE id = %s",
                (normalized, row_id),
            )

    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize RO values in assignment tables.")
    parser.add_argument("--dry-run", action="store_true", help="Show counts without writing updates")
    args = parser.parse_args()

    conn = get_conn()
    cur = conn.cursor()
    try:
        labor_count = normalize_table(cur, "labor_assignments", args.dry_run)
        refinish_count = normalize_table(cur, "refinish_assignments", args.dry_run)

        if args.dry_run:
            print(f"[dry-run] labor_assignments: {labor_count} rows would be updated")
            print(f"[dry-run] refinish_assignments: {refinish_count} rows would be updated")
        else:
            conn.commit()
            print(f"labor_assignments: {labor_count} rows updated")
            print(f"refinish_assignments: {refinish_count} rows updated")
    finally:
        cur.close()


if __name__ == "__main__":
    main()
