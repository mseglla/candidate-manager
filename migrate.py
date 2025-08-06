import os
import sqlite3

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")


def migrate(db_name=None):
    """Apply pending SQL migrations in order."""
    if db_name is None:
        db_name = os.getenv("DB_NAME", "candidates.db")
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY)"
    )
    applied = {
        row[0] for row in cur.execute("SELECT version FROM schema_migrations")
    }
    migrations = [
        f
        for f in sorted(os.listdir(MIGRATIONS_DIR))
        if f.endswith(".sql")
    ]
    for fname in migrations:
        version = fname.split("_")[0]
        if version in applied:
            continue
        path = os.path.join(MIGRATIONS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()
        cur.executescript(sql)
        cur.execute(
            "INSERT INTO schema_migrations(version) VALUES (?)", (version,)
        )
        print(f"Applied migration {fname}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    migrate()
