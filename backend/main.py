from fastapi import FastAPI
from db import init_db, get_conn, seed_data
from fastapi.middleware.cors import CORSMiddleware
import requests  # 👈 ADD THIS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
seed_data()


# =========================
# PSA FETCH FUNCTION (NEW)
# =========================
def fetch_psa_summary(spec_id: int):
    url = f"https://www.psacard.com/api/psa/researchJourney/spec/{spec_id}/psa/priceSummary"

    params = {
        "salesSummaryType": "GRADES",
        "q": "false",
        "gt": "SINGLE_GRADED"
    }

    r = requests.get(url, params=params)

    print("STATUS:", r.status_code)
    print("HEADERS:", r.headers.get("content-type"))
    print("TEXT PREVIEW:", r.text[:500])

    return r


# =========================
# IMPORT ENDPOINT (NEW STEP 1)
# =========================
@app.post("/import/{spec_id}")
def import_spec(spec_id: int):
    r = fetch_psa_summary(spec_id)

    return {
        "status_code": r.status_code,
        "content_type": r.headers.get("content-type"),
        "preview": r.text[:300]
    }


# =========================
# EXISTING ENDPOINTS (UNCHANGED)
# =========================
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