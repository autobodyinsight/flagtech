#!/usr/bin/env python3
"""Initialize the users table in the database."""

from app.services.db import get_conn

def init_users_table():
    """Create the users table if it doesn't exist."""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Check if users table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            )
        """)
        table_exists = cur.fetchone()['exists']
        
        if table_exists:
            # Table exists, check if domain column exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'domain'
                )
            """)
            domain_exists = cur.fetchone()['exists']
            
            if not domain_exists:
                # Add domain column to users table
                cur.execute("""
                    ALTER TABLE users 
                    ADD COLUMN domain VARCHAR(255)
                """)
                print("✓ Added domain column to users table")
            else:
                print("✓ Domain column already exists in users table")
        else:
            # Create users table
            cur.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    domain VARCHAR(255) NOT NULL,
                    company_name VARCHAR(255) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE
                )
            """)
            print("✓ Created users table")
        
        # Create index on email
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        
        # Create index on domain
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_domain ON users(domain)
        """)
        
        # Add domain column to techs table if needed
        try:
            cur.execute("""
                ALTER TABLE techs 
                ADD COLUMN domain VARCHAR(255)
            """)
            print("✓ Added domain column to techs table")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("✓ Domain column already exists in techs table")
            else:
                raise
        
        # Create parts vendors table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS parts_vendors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                vendor_type VARCHAR(100),
                contact_person VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(50),
                street VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(100),
                zip VARCHAR(20),
                domain VARCHAR(255) NOT NULL,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_parts_vendors_domain ON parts_vendors(domain)
        """)

        # Create sessions table for persistent logins
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token VARCHAR(255) PRIMARY KEY,
                user_id INTEGER,
                email VARCHAR(255),
                domain VARCHAR(255),
                company_name VARCHAR(255),
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)
        """)
        
        conn.commit()
        print("✓ Database schema updated successfully!")
        
        # Check if table has users
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()['count']
        print(f"✓ Current users count: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()

if __name__ == "__main__":
    init_users_table()
