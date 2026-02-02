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
        
        # Add domain column to labor_assignments table if needed
        try:
            cur.execute("""
                ALTER TABLE labor_assignments 
                ADD COLUMN domain VARCHAR(255)
            """)
            print("✓ Added domain column to labor_assignments table")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("✓ Domain column already exists in labor_assignments table")
            else:
                raise
        
        # Add domain column to refinish_assignments table if needed
        try:
            cur.execute("""
                ALTER TABLE refinish_assignments 
                ADD COLUMN domain VARCHAR(255)
            """)
            print("✓ Added domain column to refinish_assignments table")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("✓ Domain column already exists in refinish_assignments table")
            else:
                raise
        
        # Create indexes on domain columns
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_techs_domain ON techs(domain)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_labor_domain ON labor_assignments(domain)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_refinish_domain ON refinish_assignments(domain)
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
