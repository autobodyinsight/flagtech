#!/usr/bin/env python3
"""Seed or update login users for FlagTech."""

import argparse
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.auth import upsert_user


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed FlagTech users")
    parser.add_argument("--password", required=True, help="Password to assign to seeded users")
    args = parser.parse_args()

    users = [
        ("jorge@autobodyinsight.com", "AutoBody Insight"),
        ("702serrano.jorge@gmail.com", "AutoBody Insight"),
    ]

    for email, company in users:
        upsert_user(email=email, password=args.password, company_name=company, active=True)
        print(f"Upserted: {email}")


if __name__ == "__main__":
    main()
