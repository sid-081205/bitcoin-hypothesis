"""Build an independent NLP sentiment index for Bitcoin.

Pipeline:
  1. Pull every Hacker News story mentioning bitcoin/btc since 2018 from the
     Algolia HN Search API (free, no key), month by month.
  2. Score each headline with VADER, a lexicon + rule-based NLP sentiment model.
  3. Aggregate monthly: mean compound score, % positive / % negative headlines,
     and story volume (media attention).

This gives a text-derived sentiment series that is methodologically independent
of the market-derived Fear & Greed index (which is built from volatility,
volume, dominance, etc. -- not language). Cross-referencing the two tests
whether "bad sentiment" in actual written coverage adds any information.
"""

import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://hn.algolia.com/api/v1/search_by_date"
RELEVANT = re.compile(r"\b(bitcoin|btc|crypto|cryptocurrency|cryptocurrencies)\b", re.I)

# VADER's lexicon doesn't know crypto/finance jargon; extend it with
# domain terms (weights on VADER's -4..+4 scale, conservative magnitudes).
DOMAIN_LEXICON = {
    "bullish": 2.0, "bearish": -2.0, "rally": 1.5, "rallies": 1.5, "surge": 1.8,
    "surges": 1.8, "soars": 2.0, "soar": 2.0, "plunge": -2.0, "plunges": -2.0,
    "plummet": -2.2, "plummets": -2.2, "crash": -2.5, "crashes": -2.5,
    "tumble": -1.8, "tumbles": -1.8, "slump": -1.6, "slumps": -1.6,
    "selloff": -1.8, "sell-off": -1.8, "liquidation": -1.5, "liquidated": -1.8,
    "all-time": 1.0, "ath": 1.5, "hack": -2.2, "hacked": -2.5, "scam": -2.8,
    "fraud": -2.8, "ponzi": -3.0, "ban": -1.8, "bans": -1.8, "banned": -1.8,
    "bankrupt": -3.0, "bankruptcy": -3.0, "collapse": -2.5, "collapses": -2.5,
    "adoption": 1.5, "adopts": 1.5, "approve": 1.5, "approves": 1.8,
    "approval": 1.5, "etf": 0.5, "halving": 0.5, "outflow": -1.2,
    "outflows": -1.2, "inflow": 1.2, "inflows": 1.2, "bubble": -1.5,
    "dead": -2.0, "dies": -2.0, "record": 1.0, "milestone": 1.2,
}


def fetch_month(start_ts: int, end_ts: int) -> list[dict]:
    params = {
        "query": "bitcoin",
        "tags": "story",
        "hitsPerPage": 1000,
        "numericFilters": f"created_at_i>={start_ts},created_at_i<{end_ts}",
    }
    for attempt in range(3):
        r = requests.get(API, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()["hits"]
        time.sleep(2 * (attempt + 1))
    r.raise_for_status()
    return []


def main():
    analyzer = SentimentIntensityAnalyzer()
    analyzer.lexicon.update(DOMAIN_LEXICON)

    months = pd.date_range("2018-01-01", datetime.now(timezone.utc).strftime("%Y-%m-%d"), freq="MS")
    rows = []
    raw_count = 0
    for i, m0 in enumerate(months):
        m1 = m0 + pd.DateOffset(months=1)
        hits = fetch_month(int(m0.timestamp()), int(m1.timestamp()))
        raw_count += len(hits)
        scores = []
        for h in hits:
            title = (h.get("title") or "").strip()
            if not title or not RELEVANT.search(title):
                continue
            scores.append(analyzer.polarity_scores(title)["compound"])
        if scores:
            s = pd.Series(scores)
            rows.append(
                {
                    "date": m0.strftime("%Y-%m"),
                    "mean_compound": round(float(s.mean()), 4),
                    "pct_positive": round(float((s > 0.05).mean()) * 100, 1),
                    "pct_negative": round(float((s < -0.05).mean()) * 100, 1),
                    "n_headlines": len(scores),
                }
            )
        if (i + 1) % 12 == 0:
            print(f"  {m0.strftime('%Y-%m')}: {raw_count} stories fetched so far")
        time.sleep(0.4)

    df = pd.DataFrame(rows)
    df.to_csv(DATA / "nlp_sentiment_monthly.csv", index=False)
    print(f"scored {df['n_headlines'].sum()} relevant headlines across {len(df)} months")
    print(df.tail(8).to_string(index=False))


if __name__ == "__main__":
    main()
