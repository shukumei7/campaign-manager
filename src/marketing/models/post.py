"""Posted content CRUD operations."""

from marketing.db import get_connection


def _row_to_dict(row) -> dict | None:
    return dict(row) if row else None


def create_post(draft_id: int, channel: str, external_id: str = None, external_url: str = None) -> dict:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO posts (draft_id, channel, external_id, external_url) VALUES (?, ?, ?, ?)",
        (draft_id, channel, external_id, external_url),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM posts WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def get_post(post_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def get_post_by_draft(draft_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM posts WHERE draft_id = ?", (draft_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def list_posts(channel: str = None) -> list[dict]:
    conn = get_connection()
    if channel:
        rows = conn.execute("SELECT * FROM posts WHERE channel = ? ORDER BY posted_at DESC", (channel,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM posts ORDER BY posted_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]
