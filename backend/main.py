from fastapi import FastAPI
from db import init_db, get_conn, seed_data
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright
import json
import math
from datetime import datetime

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

        response = context.request.get(
        url,
        params=params,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.psacard.com/",
        }
    )
        text = response.text()
        print("RAW RESPONSE:")
        print(text[:1000])

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

            avg = m.get("averagePrice")
            latest = m.get("latestPrice")
            qty = m.get("quantity") or 0

            if avg and latest:
                momentum = ((latest - avg) / avg) + math.log(1 + qty)
            else:
                momentum = 0

            cleaned.append({
                "date": point.get("date"),
                "avg": avg,
                "latest": latest,
                "qty": qty,
                "momentum": momentum
            })

        return cleaned


# =========================
# 🔥 SNAPSHOT REFRESH FUNCTION (PUT HERE)
# =========================
def refresh_snapshots():
    conn = get_conn()
    c = conn.cursor()

    rows = c.execute("""
        SELECT spec_id, name FROM cards
    """).fetchall()

    for spec_id, name in rows:

        print("Refreshing:", spec_id)

        series = fetch_psa_timeseries(spec_id)

        print("Series length:", len(series))

        if not series:
            print("No data for:", spec_id)
            continue

        last = series[-1]

        print("Last:", last)

        c.execute("""
            INSERT INTO card_snapshot (spec_id, name, avg, latest, momentum, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(spec_id) DO UPDATE SET
                name=excluded.name,
                avg=excluded.avg,
                latest=excluded.latest,
                momentum=excluded.momentum,
                updated_at=excluded.updated_at
        """, (
            spec_id,
            name,
            last.get("avg"),
            last.get("latest"),
            last.get("momentum"),
            datetime.utcnow().isoformat()
        ))

    conn.commit()
    conn.close()


# =========================
# IMPORT ENDPOINT
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
# CARDS (SNAPSHOT SYSTEM - FAST DASHBOARD)
# =========================
@app.get("/cards")
def cards():
    conn = get_conn()
    c = conn.cursor()

    rows = c.execute("""
        SELECT spec_id, name, avg, latest, momentum, updated_at
        FROM card_snapshot
        ORDER BY momentum DESC
    """).fetchall()

    conn.close()

    return [
        {
            "spec_id": r[0],
            "name": r[1],
            "avg": r[2],
            "latest": r[3],
            "momentum": r[4],
            "updated_at": r[5],
        }
        for r in rows
    ]


# =========================
# CARD TIMESERIES
# =========================
@app.get("/card/{spec_id}")
def card(spec_id: int):
    return {
        "spec_id": spec_id,
        "timeseries": fetch_psa_timeseries(spec_id)
    }


# =========================
# 🔥 NEW: MANUAL REFRESH ENDPOINT
# =========================
@app.get("/refresh")
@app.post("/refresh")
def refresh():
    refresh_snapshots()
    return {"status": "ok"}