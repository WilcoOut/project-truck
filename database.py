import sqlite3
import json
from datetime import datetime
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS listings (
            id          TEXT PRIMARY KEY,
            source      TEXT NOT NULL,
            url         TEXT NOT NULL,
            title       TEXT,
            price       INTEGER,
            location    TEXT,
            description TEXT,
            image_url   TEXT,
            year        INTEGER,
            make        TEXT,
            model       TEXT,
            score       REAL,
            green_flags TEXT,
            red_flags   TEXT,
            first_seen  TEXT,
            last_seen   TEXT,
            is_new      INTEGER DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_score      ON listings(score DESC);
        CREATE INDEX IF NOT EXISTS idx_first_seen ON listings(first_seen DESC);
        CREATE INDEX IF NOT EXISTS idx_is_new     ON listings(is_new DESC);
    """)
    conn.commit()
    conn.close()


def upsert_listing(listing: dict) -> bool:
    """Insert or update a listing. Returns True if it was brand-new."""
    conn = get_conn()
    now = datetime.now().isoformat()
    existing = conn.execute(
        "SELECT id FROM listings WHERE id = ?", (listing["id"],)
    ).fetchone()

    is_new = existing is None

    if is_new:
        conn.execute(
            """
            INSERT INTO listings
                (id, source, url, title, price, location, description,
                 image_url, year, make, model, score, green_flags, red_flags,
                 first_seen, last_seen, is_new)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)
            """,
            (
                listing["id"], listing["source"], listing["url"],
                listing.get("title"), listing.get("price"),
                listing.get("location"), listing.get("description"),
                listing.get("image_url"), listing.get("year"),
                listing.get("make"), listing.get("model"),
                listing.get("score"),
                json.dumps(listing.get("green_flags", [])),
                json.dumps(listing.get("red_flags", [])),
                now, now,
            ),
        )
    else:
        conn.execute(
            "UPDATE listings SET last_seen=?, score=? WHERE id=?",
            (now, listing.get("score"), listing["id"]),
        )

    conn.commit()
    conn.close()
    return is_new


def get_all_listings(limit: int = 300) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT * FROM listings
        ORDER BY is_new DESC, score DESC, first_seen DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["green_flags"] = json.loads(d["green_flags"] or "[]")
        d["red_flags"] = json.loads(d["red_flags"] or "[]")
        result.append(d)
    return result


def reset_new_flags() -> None:
    """Clear is_new before each run so only today's finds are flagged new."""
    conn = get_conn()
    conn.execute("UPDATE listings SET is_new=0")
    conn.commit()
    conn.close()


def cleanup_stale_listings(days: int = 3) -> int:
    """Delete listings not seen in the last `days` days. Returns count removed."""
    conn = get_conn()
    result = conn.execute(
        "DELETE FROM listings WHERE last_seen < datetime('now', ?)",
        (f"-{days} days",),
    )
    removed = result.rowcount
    conn.commit()
    conn.close()
    return removed


def get_stats() -> dict:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    new = conn.execute("SELECT COUNT(*) FROM listings WHERE is_new=1").fetchone()[0]
    rows = conn.execute(
        "SELECT make, COUNT(*) as cnt FROM listings GROUP BY make ORDER BY make"
    ).fetchall()
    conn.close()
    return {"total": total, "new": new, "by_make": {r["make"]: r["cnt"] for r in rows}}
