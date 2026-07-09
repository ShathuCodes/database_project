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


def run_in_transaction(fn):
    """Run a callback that receives a live cursor, committing at the end
       (or rolling back on any exception). Used for multi-table subtype
       inserts such as CASE_EVENT + POSTMORTEM/CLINICAL_EXAMINATION/SKELETAL_EXAMINATION."""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        result = fn(cur)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def log_action(user_id, action_type, table_name, record_id=None,
                old_values=None, new_values=None, ip=None):
    """Write to audit_log table. action_type must be INSERT / UPDATE / DELETE."""
    execute(
        """INSERT INTO audit_log (user_id, table_name, record_id, action_type,
                                   old_values, new_values, ip_address)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (user_id, table_name, record_id, action_type, old_values, new_values, ip)
    )


def notify(user_id, title, message_text):
    """Insert a NOTIFICATION row for a user."""
    execute(
        "INSERT INTO notification (user_id, title, message_text) VALUES (%s,%s,%s)",
        (user_id, title, message_text)
    )
