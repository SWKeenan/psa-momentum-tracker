import sqlite3

DB = "psa.db"


def get_conn():
    return sqlite3.connect(DB)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # =========================
    # CORE TABLES
    # =========================
    c.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        spec_id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        spec_id INTEGER,
        date TEXT,
        price REAL
    )
    """)

    # =========================
    # SNAPSHOT TABLE (NEW)
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


def seed_data():
    conn = get_conn()
    c = conn.cursor()

    # =========================
    # REAL PSA CARDS
    # Replace these with cards you actually want to track
    # =========================
    c.execute("INSERT OR IGNORE INTO cards VALUES (2306882, 'Scizor PSA Test')")
    c.execute("INSERT OR IGNORE INTO cards VALUES (11847394, 'Pikachu Promo')")

    conn.commit()
    conn.close()