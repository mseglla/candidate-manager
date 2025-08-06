import sqlite3

DB_NAME = "candidates.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(candidate_id) REFERENCES candidates(id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY(candidate_id) REFERENCES candidates(id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            activity_date TEXT NOT NULL,
            FOREIGN KEY(candidate_id) REFERENCES candidates(id)
        )
        """
    )
    conn.commit()
    conn.close()
