"""Campaign CRUD operations."""

from datetime import datetime, timezone
from marketing.db import get_connection


def _row_to_dict(row) -> dict | None:
    return dict(row) if row else None


def create_campaign(name: str, description: str = "") -> dict:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO campaigns (name, description) VALUES (?, ?)",
        (name, description),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM campaigns WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def get_campaign(campaign_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def get_campaign_by_name(name: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM campaigns WHERE name = ?", (name,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def list_campaigns(status: str = None) -> list[dict]:
    conn = get_connection()
    if status:
        rows = conn.execute("SELECT * FROM campaigns WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM campaigns ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_campaign_status(campaign_id: int, status: str) -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE campaigns SET status = ?, updated_at = ? WHERE id = ?",
        (status, now, campaign_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)
