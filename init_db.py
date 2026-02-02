#!/usr/bin/env python3
"""Initialize the users table in the database."""

from app.services.db import get_conn

def init_users_table():
    """Create the users table if it doesn't exist."""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Create index on email
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        
        conn.commit()
        print("✓ Users table created successfully!")
        
        # Check if table is empty
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        print(f"✓ Current users count: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating users table: {e}")
    finally:
        cur.close()

if __name__ == "__main__":
    init_users_table()
