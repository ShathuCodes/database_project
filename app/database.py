import psycopg2
import psycopg2.extras
from app.config import Config


def get_connection():
    """Return a new PostgreSQL connection."""
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )


def fetchall(sql, params=None):
    """Execute SELECT and return list of dicts."""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def fetchone(sql, params=None):
    """Execute SELECT and return single dict or None."""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def execute(sql, params=None, returning=False):
    """Execute INSERT / UPDATE / DELETE. If returning=True, returns the first row."""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        result = None
        if returning:
            result = dict(cur.fetchone())
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def log_action(user_id, action, table_name, record_id=None, details=None, ip=None):
    """Write to audit_log table."""
    execute(
        """INSERT INTO audit_log (user_id, action, table_name, record_id, details, ip_address)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (user_id, action, table_name, record_id, details, ip)
    )