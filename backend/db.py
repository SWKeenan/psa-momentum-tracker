import sqlite3

DB = "psa.db"


def get_conn():
    return sqlite3.connect(DB)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # =========================
    # CARDS (auto-filled via /import)
    # =========================
    c.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        spec_id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    # =========================
    # SNAPSHOT TABLE (dashboard speed layer)
    # =========================
    c.execute("""
    CREATE TABLE IF NOT EXISTS card_snapshot (
        spec_id INTEGER PRIMARY KEY,
        name TEXT,
        avg REAL,
        latest REAL,
        momentum REAL,
        updated_at TEXT
    )
    """)

    conn.commit()
    conn.close()