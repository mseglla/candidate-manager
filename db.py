import os
import sqlite3

DB_NAME = os.getenv("DB_NAME", "candidates.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Apply pending database migrations."""
    from migrate import migrate

    migrate(DB_NAME)
