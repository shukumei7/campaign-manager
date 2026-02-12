"""Metrics snapshot CRUD operations."""

import json
from marketing.db import get_connection


def _row_to_dict(row) -> dict | None:
    return dict(row) if row else None


def add_metric(post_id: int, upvotes: int = 0, comments: int = 0, views: int = 0, extra: dict = None) -> dict:
    conn = get_connection()
    extra_json = json.dumps(extra or {})
    cursor = conn.execute(
        "INSERT INTO metrics (post_id, upvotes, comments, views, extra_json) VALUES (?, ?, ?, ?, ?)",
        (post_id, upvotes, comments, views, extra_json),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM metrics WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def get_latest_metric(post_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM metrics WHERE post_id = ? ORDER BY captured_at DESC LIMIT 1",
        (post_id,),
    ).fetchone()
    conn.close()
    return _row_to_dict(row)


def list_metrics(post_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM metrics WHERE post_id = ? ORDER BY captured_at ASC",
        (post_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
