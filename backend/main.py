from fastapi import FastAPI
from db import init_db, get_conn, seed_data
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright
import json

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
# PSA TIMESERIES FETCH (PLAYWRIGHT)
# =========================
def fetch_psa_timeseries(spec_id: int):
    url = f"https://www.psacard.com/api/psa/researchJourney/spec/{spec_id}/psa/priceSummary"

    params = {
        "g": 10,
        "tr": 0,
        "salesSummaryType": "TIMESERIES",
        "q": "false",
        "gt": "SINGLE_GRADED"
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()

        # ✅ IMPORTANT: use API request instead of page.goto
        response = context.request.get(url, params=params)

        text = response.text()

        browser.close()

        if not text or not text.strip().startswith("{"):
            print("BLOCKED RESPONSE:", text[:300])
            return []

        try:
            data = json.loads(text)
        except Exception as e:
            print("JSON ERROR:", e)
            return []

        series = data.get("salesSummary", [])

        cleaned = []
        for point in series:
            m = point.get("metrics", {})
            cleaned.append({
                "date": point.get("date"),
                "avg": m.get("averagePrice"),
                "latest": m.get("latestPrice"),
                "qty": m.get("quantity")
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
        "sample": series[-3:] if len(series) >= 3 else series
    }


# =========================
# CARDS (OLD SYSTEM - leaderboard)
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
# CARD TIMESERIES (FRONTEND)
# =========================
@app.get("/card/{spec_id}")
def card(spec_id: int):
    return {
        "spec_id": spec_id,
        "timeseries": fetch_psa_timeseries(spec_id)
    }