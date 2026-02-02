"""Authentication service for user management."""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from app.services.db import get_conn


def extract_domain(email: str) -> str:
    """Extract domain from email address."""
    return email.split('@')[1].lower() if '@' in email else ''


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == password_hash


def create_user(email: str, company_name: str, password: str) -> Dict:
    """Create a new user account."""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Extract domain from email
        domain = extract_domain(email)
        if not domain:
            return {"success": False, "error": "Invalid email address"}
        
        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return {"success": False, "error": "Email already registered"}
        
        # Hash password and create user
        password_hash = hash_password(password)
        cur.execute("""
            INSERT INTO users (email, domain, company_name, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, domain, company_name, created_at
        """, (email, domain, company_name, password_hash))
        
        user = cur.fetchone()
        conn.commit()
        
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "domain": user["domain"],
                "company_name": user["company_name"],
                "created_at": str(user["created_at"])
            }
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cur.close()


def authenticate_user(email: str, password: str) -> Dict:
    """Authenticate a user with email and password."""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, email, domain, company_name, password_hash, active
            FROM users
            WHERE email = %s
        """, (email,))
        
        user = cur.fetchone()
        
        if not user:
            return {"success": False, "error": "Invalid email or password"}
        
        if not user["active"]:
            return {"success": False, "error": "Account is inactive"}
        
        if not verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Invalid email or password"}
        
        # Update last login
        cur.execute("""
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (user["id"],))
        conn.commit()
        
        # Generate session token
        token = secrets.token_urlsafe(32)
        
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "domain": user["domain"],
                "company_name": user["company_name"]
            },
            "token": token
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cur.close()


def get_user_by_token(token: str) -> Optional[Dict]:
    """Get user information by session token.
    Note: This is a simple implementation. In production, use Redis or a sessions table.
    """
    # For now, we'll store sessions in memory (this will reset on server restart)
    # In production, you should use a proper session store
    return None


def store_session(token: str, user_data: Dict, ttl_days: int = 7) -> None:
    """Store session data in the database."""
    conn = get_conn()
    cur = conn.cursor()
    expires_at = datetime.utcnow() + timedelta(days=ttl_days)

    try:
        cur.execute(
            """
            INSERT INTO sessions (token, user_id, email, domain, company_name, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (token)
            DO UPDATE SET
                user_id = EXCLUDED.user_id,
                email = EXCLUDED.email,
                domain = EXCLUDED.domain,
                company_name = EXCLUDED.company_name,
                expires_at = EXCLUDED.expires_at
            """,
            (
                token,
                user_data.get("user_id"),
                user_data.get("email"),
                user_data.get("domain"),
                user_data.get("company_name"),
                expires_at,
            ),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def get_session(token: str) -> Optional[Dict]:
    """Get session data by token from the database."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT token, user_id, email, domain, company_name, expires_at
            FROM sessions
            WHERE token = %s
            """,
            (token,),
        )
        row = cur.fetchone()
        if not row:
            return None

        expires_at = row.get("expires_at")
        if expires_at and expires_at < datetime.utcnow():
            cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
            conn.commit()
            return None

        return {
            "token": row.get("token"),
            "user_id": row.get("user_id"),
            "email": row.get("email"),
            "domain": row.get("domain"),
            "company_name": row.get("company_name"),
        }
    finally:
        cur.close()


def delete_session(token: str) -> None:
    """Delete session data from the database."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
