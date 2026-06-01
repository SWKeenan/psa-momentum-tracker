from fastapi import FastAPI
from db import init_db, get_conn, seed_data
from fastapi.middleware.cors import CORSMiddleware

// Test comment
app = FastAPI()

# 👇 ADD THIS BLOCK RIGHT HERE (after app = FastAPI)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
seed_data()

@app.get("/cards")
def cards():
    conn = get_conn()
    c = conn.cursor()

    rows = c.execute("""
        SELECT c.spec_id, c.name,
        COALESCE(AVG(s.price),0) as avg_price
        FROM cards c
        LEFT JOIN sales s ON c.spec_id = s.spec_id
        GROUP BY c.spec_id
        ORDER BY avg_price DESC
    """).fetchall()

    conn.close()

    return [
        {"spec_id": r[0], "name": r[1], "avg": r[2]}
        for r in rows
    ]


@app.get("/card/{spec_id}")
def card(spec_id: int):
    conn = get_conn()
    c = conn.cursor()

    rows = c.execute("""
        SELECT date, price
        FROM sales
        WHERE spec_id = ?
        ORDER BY date
    """, (spec_id,)).fetchall()

    conn.close()

    return {"sales": rows}