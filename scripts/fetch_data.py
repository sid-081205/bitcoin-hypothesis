"""Fetch all raw data for the Bitcoin Hypothesis project.

Sources (all free, no API keys):
  - Yahoo Finance (via yfinance): BTC-USD, S&P 500, NASDAQ, Gold futures, DXY
  - FRED CSV endpoint: Fed funds rate, 10Y treasury yield, M2 money supply, CPI
  - alternative.me: Crypto Fear & Greed index (daily, since Feb 2018)
  - blockchain.info charts API: network hash rate, unique addresses
"""

import io
import json
import time
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)

UA = {"User-Agent": "bitcoin-hypothesis-research/1.0"}


def fetch_yahoo():
    tickers = {
        "BTC-USD": "btc",
        "^GSPC": "sp500",
        "^IXIC": "nasdaq",
        "GC=F": "gold",
        "DX-Y.NYB": "dxy",
    }
    for ticker, name in tickers.items():
        df = yf.download(ticker, start="2014-01-01", auto_adjust=True, progress=False)
        if df.empty:
            raise RuntimeError(f"empty download for {ticker}")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        out = df[["Close"]].rename(columns={"Close": "close"})
        out.index.name = "date"
        out.to_csv(DATA / f"{name}.csv")
        print(f"{name}: {len(out)} rows ({out.index.min().date()} -> {out.index.max().date()})")
        time.sleep(1)


def fetch_fred():
    series = {
        "DFF": "fed_funds",       # effective federal funds rate, daily
        "DGS10": "treasury_10y",  # 10-year treasury constant maturity, daily
        "M2SL": "m2",             # M2 money supply, monthly
        "CPIAUCSL": "cpi",        # CPI all urban consumers, monthly
    }
    for sid, name in series.items():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        r = requests.get(url, headers=UA, timeout=60)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "value"]
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()
        df.to_csv(DATA / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} rows (through {df['date'].iloc[-1]})")


def fetch_fear_greed():
    r = requests.get("https://api.alternative.me/fng/?limit=0&format=json", headers=UA, timeout=60)
    r.raise_for_status()
    rows = r.json()["data"]
    df = pd.DataFrame(
        {
            "date": pd.to_datetime([int(x["timestamp"]) for x in rows], unit="s"),
            "value": [int(x["value"]) for x in rows],
            "label": [x["value_classification"] for x in rows],
        }
    ).sort_values("date")
    df.to_csv(DATA / "fear_greed.csv", index=False)
    print(f"fear_greed: {len(df)} rows (through {df['date'].iloc[-1].date()})")


def fetch_blockchain_info():
    charts = {"hash-rate": "hash_rate", "n-unique-addresses": "active_addresses"}
    for chart, name in charts.items():
        url = f"https://api.blockchain.info/charts/{chart}?timespan=all&format=json&sampled=true"
        r = requests.get(url, headers=UA, timeout=60)
        r.raise_for_status()
        vals = r.json()["values"]
        df = pd.DataFrame(
            {
                "date": pd.to_datetime([v["x"] for v in vals], unit="s"),
                "value": [v["y"] for v in vals],
            }
        )
        df.to_csv(DATA / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} rows (through {df['date'].iloc[-1].date()})")


if __name__ == "__main__":
    fetch_yahoo()
    fetch_fred()
    fetch_fear_greed()
    fetch_blockchain_info()
    print("done")
