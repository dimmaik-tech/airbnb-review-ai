import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("host_reply_pro.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH.as_posix(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS kv (
        k TEXT PRIMARY KEY,
        v TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT DEFAULT "",
        location TEXT DEFAULT "",
        checkin TEXT DEFAULT "",
        checkout TEXT DEFAULT "",
        house_rules TEXT DEFAULT "",
        amenities TEXT DEFAULT ""
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        property_name TEXT DEFAULT "",
        platform TEXT NOT NULL,
        tone TEXT NOT NULL,
        language TEXT NOT NULL,
        length TEXT NOT NULL,
        sentiment TEXT NOT NULL,
        issues_json TEXT NOT NULL,
        summary TEXT NOT NULL,
        highlights_json TEXT NOT NULL,
        review TEXT NOT NULL,
        reply TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def kv_get(key: str) -> Optional[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT v FROM kv WHERE k=?", (key,))
    row = cur.fetchone()
    conn.close()
    return row["v"] if row else None


def kv_set(key: str, value: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO kv (k, v) VALUES (?, ?)
        ON CONFLICT(k) DO UPDATE SET v=excluded.v
    """, (key, value))
    conn.commit()
    conn.close()


def list_properties() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM properties ORDER BY name COLLATE NOCASE")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_property(data: Dict[str, Any]) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO properties (name, description, location, checkin, checkout, house_rules, amenities)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            description=excluded.description,
            location=excluded.location,
            checkin=excluded.checkin,
            checkout=excluded.checkout,
            house_rules=excluded.house_rules,
            amenities=excluded.amenities
    """, (
        data["name"],
        data.get("description", ""),
        data.get("location", ""),
        data.get("checkin", ""),
        data.get("checkout", ""),
        data.get("house_rules", ""),
        data.get("amenities", ""),
    ))
    conn.commit()
    conn.close()


def delete_property(name: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM properties WHERE name=?", (name,))
    conn.commit()
    conn.close()


def add_history(row: Dict[str, Any]) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO history (
            created_at, property_name, platform, tone, language, length,
            sentiment, issues_json, summary, highlights_json, review, reply
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["created_at"],
        row.get("property_name", ""),
        row["platform"],
        row["tone"],
        row["language"],
        row["length"],
        row["sentiment"],
        row["issues_json"],
        row["summary"],
        row["highlights_json"],
        row["review"],
        row["reply"],
    ))
    conn.commit()
    conn.close()


def list_history(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_history_item(item_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM history WHERE id=?", (item_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def clear_history() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM history")
    conn.commit()
    conn.close()
