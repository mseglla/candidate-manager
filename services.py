from db import get_connection
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Candidate Services

def create_candidate(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO candidates(name, email) VALUES (?, ?)",
        (data.get("name"), data.get("email")),
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid

def get_candidates():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidates")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def get_candidate(cid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidates WHERE id = ?", (cid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_candidate(cid, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE candidates SET name = ?, email = ? WHERE id = ?",
        (data.get("name"), data.get("email"), cid),
    )
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0

def delete_candidate(cid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM candidates WHERE id = ?", (cid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0

# Comment Services

def create_comment(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO comments(candidate_id, content) VALUES (?, ?)",
        (data.get("candidate_id"), data.get("content")),
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid

def get_comments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM comments")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def get_comment(cid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM comments WHERE id = ?", (cid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_comment(cid, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE comments SET candidate_id = ?, content = ? WHERE id = ?",
        (data.get("candidate_id"), data.get("content"), cid),
    )
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0

def delete_comment(cid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM comments WHERE id = ?", (cid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0

# Evaluation Services

def create_evaluation(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO evaluations(candidate_id, score, notes) VALUES (?, ?, ?)",
        (data.get("candidate_id"), data.get("score"), data.get("notes")),
    )
    conn.commit()
    eid = cur.lastrowid
    conn.close()
    return eid

def get_evaluations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM evaluations")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def get_evaluation(eid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM evaluations WHERE id = ?", (eid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_evaluation(eid, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE evaluations SET candidate_id = ?, score = ?, notes = ? WHERE id = ?",
        (data.get("candidate_id"), data.get("score"), data.get("notes"), eid),
    )
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0

def delete_evaluation(eid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM evaluations WHERE id = ?", (eid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0

# Activity Services

def create_activity(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO activity_history(candidate_id, description, activity_date) VALUES (?, ?, ?)",
        (data.get("candidate_id"), data.get("description"), data.get("activity_date")),
    )
    conn.commit()
    aid = cur.lastrowid
    conn.close()
    return aid


def get_activities():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activity_history")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_activity(aid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activity_history WHERE id = ?", (aid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_activity(aid, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE activity_history SET candidate_id = ?, description = ?, activity_date = ? WHERE id = ?",
        (data.get("candidate_id"), data.get("description"), data.get("activity_date"), aid),
    )
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0


def delete_activity(aid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM activity_history WHERE id = ?", (aid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0


# User Services


def create_user(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users(username, email, password, role) VALUES (?, ?, ?, ?)",
        (
            data.get("username"),
            data.get("email"),
            hash_password(data.get("password", "")),
            data.get("role", "user"),
        ),
    )
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return uid


def get_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role FROM users")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_user(uid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, email, role FROM users WHERE id = ?",
        (uid,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user(uid, data):
    conn = get_connection()
    cur = conn.cursor()
    if data.get("password"):
        cur.execute(
            "UPDATE users SET username = ?, email = ?, password = ?, role = ? WHERE id = ?",
            (
                data.get("username"),
                data.get("email"),
                hash_password(data.get("password")),
                data.get("role", "user"),
                uid,
            ),
        )
    else:
        cur.execute(
            "UPDATE users SET username = ?, email = ?, role = ? WHERE id = ?",
            (data.get("username"), data.get("email"), data.get("role", "user"), uid),
        )
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0


def delete_user(uid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (uid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0


def authenticate_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row and row["password"] == hash_password(password):
        return row["id"]
    return None


# File Services


def create_file(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files(candidate_id, filename, path, uploaded_at) VALUES (?, ?, ?, ?)",
        (
            data.get("candidate_id"),
            data.get("filename"),
            data.get("path"),
            data.get("uploaded_at"),
        ),
    )
    conn.commit()
    fid = cur.lastrowid
    conn.close()
    return fid


def get_files():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM files")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_file(fid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE id = ?", (fid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_file(fid, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE files SET candidate_id = ?, filename = ?, path = ?, uploaded_at = ? WHERE id = ?",
        (
            data.get("candidate_id"),
            data.get("filename"),
            data.get("path"),
            data.get("uploaded_at"),
            fid,
        ),
    )
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0


def delete_file(fid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM files WHERE id = ?", (fid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0
