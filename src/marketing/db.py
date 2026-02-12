"""SQLite database schema and connection management."""

import sqlite3
from marketing.config import get_db_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'paused', 'completed')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER REFERENCES campaigns(id),
    channel TEXT NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'approved', 'posted', 'failed')),
    revision INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_id INTEGER REFERENCES drafts(id),
    channel TEXT NOT NULL,
    external_id TEXT,
    external_url TEXT,
    posted_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER REFERENCES posts(id),
    upvotes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    extra_json TEXT DEFAULT '{}',
    captured_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection() -> sqlite3.Connection:
    """Get a database connection with Row factory."""
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.close()
