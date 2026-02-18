# Backfill script to set status='closed' for eligible repair orders
# Adjust the WHERE clause as needed for your business logic

import psycopg2
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://management_app_yj3h_user:VioUE4I0r3VgaBiNt920IbTXfbRT9dfc@dpg-d5qf43juibrs73c4q5o0-a.oregon-postgres.render.com/management_app_yj3h",
)

def main():
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
