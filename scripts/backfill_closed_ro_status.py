# Backfill script to set status='closed' for eligible repair orders
# Adjust the WHERE clause as needed for your business logic

import psycopg2
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
)

def main():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is required")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    # Example: close all ROs that have a picked_up date and are not already closed
    cur.execute("""
        UPDATE repair_orders
        SET status = 'closed'
        WHERE picked_up IS NOT NULL AND status != 'closed'
    """)
    print(f"Rows updated: {cur.rowcount}")
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
