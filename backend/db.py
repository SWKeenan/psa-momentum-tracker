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
    # CARDS
    # =========================
    c.execute("INSERT OR IGNORE INTO cards VALUES (1, 'Scizor Holo')")
    c.execute("INSERT OR IGNORE INTO cards VALUES (2, 'Steelix Deck Promo')")

    # =========================
    # SALES (fake momentum example)
    # =========================
    c.execute("INSERT INTO sales VALUES (1, '2026-01-01', 200)")
    c.execute("INSERT INTO sales VALUES (1, '2026-02-01', 220)")
    c.execute("INSERT INTO sales VALUES (1, '2026-03-01', 300)")
    c.execute("INSERT INTO sales VALUES (1, '2026-04-01', 450)")
    c.execute("INSERT INTO sales VALUES (1, '2026-05-01', 900)")
    c.execute("INSERT INTO sales VALUES (1, '2026-05-28', 1950)")

    conn.commit()
    conn.close()