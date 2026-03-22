import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import ADMIN_DB_CONFIG, APP_DB_CONFIG


def get_admin_connection():
    # explanation: connect to DB admin 
    return psycopg2.connect(**ADMIN_DB_CONFIG)


def get_app_connection():
    # explanation: connect to project database
    return psycopg2.connect(**APP_DB_CONFIG)


def execute_query(query: str, params=None, fetch: bool = False):
    # explanation: Hàm chạy query chung cho INSERT / UPDATE / DELETE / SELECT.
    conn = get_app_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            result = cur.fetchall() if fetch else None
        conn.commit()
        return result
    except Exception:
        # explanation: Nếu có lỗi thì rollback để tránh transaction hỏng.
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(query: str, params=None):
    # explanation: Shortcut để lấy toàn bộ rows dưới dạng dict.
    return execute_query(query, params=params, fetch=True)