"""Aggregate campaign metrics into summary reports."""

from marketing.db import get_connection
from marketing.models.metric import get_latest_metric


def campaign_summary(campaign_name: str = None) -> dict:
    """Aggregate metrics across posts, optionally filtered by campaign."""
    conn = get_connection()

    if campaign_name:
        query = """
            SELECT p.id as post_id, p.channel, p.external_url, p.external_id,
                   d.title, c.name as campaign_name
            FROM posts p
            JOIN drafts d ON p.draft_id = d.id
            JOIN campaigns c ON d.campaign_id = c.id
            WHERE c.name = ?
        """
        rows = conn.execute(query, (campaign_name,)).fetchall()
    else:
        query = """
            SELECT p.id as post_id, p.channel, p.external_url, p.external_id,
                   d.title, c.name as campaign_name
            FROM posts p
            JOIN drafts d ON p.draft_id = d.id
            JOIN campaigns c ON d.campaign_id = c.id
        """
        rows = conn.execute(query).fetchall()

    conn.close()

    totals = {"upvotes": 0, "comments": 0, "views": 0}
    channels = {}
    posts_detail = []

    for row in rows:
        row = dict(row)
        metric = get_latest_metric(row["post_id"])
        m = metric or {"upvotes": 0, "comments": 0, "views": 0}

        ch = row["channel"]
        if ch not in channels:
            channels[ch] = {"posts": 0, "upvotes": 0, "comments": 0, "views": 0}
        channels[ch]["posts"] += 1
        channels[ch]["upvotes"] += m.get("upvotes", 0)
        channels[ch]["comments"] += m.get("comments", 0)
        channels[ch]["views"] += m.get("views", 0)

        totals["upvotes"] += m.get("upvotes", 0)
        totals["comments"] += m.get("comments", 0)
        totals["views"] += m.get("views", 0)

        posts_detail.append({
            "title": row["title"],
            "channel": ch,
            "campaign": row["campaign_name"],
            "url": row["external_url"] or "",
            "metrics": {k: m.get(k, 0) for k in ("upvotes", "comments", "views")},
        })

    return {
        "total_posts": len(rows),
        "channels": channels,
        "totals": totals,
        "posts": posts_detail,
    }
