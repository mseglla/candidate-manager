import sqlite3
from db import get_connection

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
        "INSERT INTO activities(candidate_id, description, activity_date) VALUES (?, ?, ?)",
        (data.get("candidate_id"), data.get("description"), data.get("activity_date")),
    )
    conn.commit()
    aid = cur.lastrowid
    conn.close()
    return aid

def get_activities():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def get_activity(aid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities WHERE id = ?", (aid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_activity(aid, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE activities SET candidate_id = ?, description = ?, activity_date = ? WHERE id = ?",
        (data.get("candidate_id"), data.get("description"), data.get("activity_date"), aid),
    )
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0

def delete_activity(aid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM activities WHERE id = ?", (aid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0
