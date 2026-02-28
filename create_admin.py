import os

EMAIL = "MY_EMAIL_HERE"
PASSWORD_HASH = "$2b$12$hvdQq9bPiG4L42XUPiH0aeATRvSP0bzh0sYN4L6Zza353hIJbm2Ua"
ROLE = "architect"


def main() -> int:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set")
        return 1

    from app.services.db import get_conn

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 1
        FROM users
        WHERE lower(email) = lower(%s)
        LIMIT 1
        """,
        (EMAIL,),
    )
    if cur.fetchone():
        print("User exists")
        cur.close()
        return 0

    cur.execute(
        """
        INSERT INTO users (email, password_hash, role, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        """,
        (EMAIL, PASSWORD_HASH, ROLE),
    )
    cur.close()
    print("User created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
