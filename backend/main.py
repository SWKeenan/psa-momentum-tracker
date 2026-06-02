from fastapi import FastAPI
from db import init_db, get_conn, seed_data
from fastapi.middleware.cors import CORSMiddleware
import requests

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
# PSA TIMESERIES FETCH
# =========================
def fetch_psa_timeseries(spec_id: int):
    import requests

    url = f"https://www.psacard.com/api/psa/researchJourney/spec/{spec_id}/psa/priceSummary"

    params = {
        "g": "",   # REMOVE grade filter
        "tr": 0,
        "salesSummaryType": "TIMESERIES",
        "q": "false",
        "gt": "SINGLE_GRADED"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.psacard.com/"
    }

    r = requests.get(url, params=params, headers=headers)

    print("STATUS:", r.status_code)
    print("RAW TEXT:", r.text[:500])

    try:
        data = r.json()
    except Exception as e:
        print("JSON ERROR:", e)
        return []

    print("JSON KEYS:", data.keys())

    series = data.get("salesSummary", [])
    print("SERIES LENGTH:", len(series))

    cleaned = []
    for point in series:
        m = point["metrics"]
        cleaned.append({
            "date": point["date"],
            "avg": m["averagePrice"],
            "latest": m["latestPrice"],
            "qty": m["quantity"]
        })

    return cleaned


# =========================
# IMPORT ENDPOINT (DEBUG / INGESTION)
# =========================
@app.post("/import/{spec_id}")
def import_spec(spec_id: int):
    series = fetch_psa_timeseries(spec_id)

    return {
        "spec_id": spec_id,
        "points": len(series),
        "sample": series[-3:]
    }


# =========================
# CARDS (OLD SYSTEM - still used for leaderboard)
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


# =========================
# CARD TIMESERIES (NEW FRONTEND DATA)
# =========================
@app.get("/card/{spec_id}")
def card(spec_id: int):
    return {
        "spec_id": spec_id,
        "timeseries": fetch_psa_timeseries(spec_id)
    }