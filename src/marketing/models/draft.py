"""Draft CRUD operations and lifecycle management."""

import json
from datetime import datetime, timezone
from marketing.db import get_connection


def _row_to_dict(row) -> dict | None:
    return dict(row) if row else None


def add_draft(campaign_id: int, channel: str, title: str, file_path: str, metadata: dict = None) -> dict:
    conn = get_connection()
    metadata_json = json.dumps(metadata or {})
    cursor = conn.execute(
        "INSERT INTO drafts (campaign_id, channel, title, file_path, metadata_json) VALUES (?, ?, ?, ?, ?)",
        (campaign_id, channel, title, file_path, metadata_json),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM drafts WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def get_draft(draft_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def list_drafts(campaign_id: int = None, channel: str = None, status: str = None) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM drafts WHERE 1=1"
    params = []
    if campaign_id is not None:
        query += " AND campaign_id = ?"
        params.append(campaign_id)
    if channel:
        query += " AND channel = ?"
        params.append(channel)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def approve_draft(draft_id: int) -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE drafts SET status = 'approved', updated_at = ? WHERE id = ?",
        (now, draft_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def mark_posted(draft_id: int) -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE drafts SET status = 'posted', updated_at = ? WHERE id = ?",
        (now, draft_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def mark_failed(draft_id: int) -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE drafts SET status = 'failed', updated_at = ? WHERE id = ?",
        (now, draft_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def increment_revision(draft_id: int) -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE drafts SET revision = revision + 1, updated_at = ? WHERE id = ?",
        (now, draft_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)
