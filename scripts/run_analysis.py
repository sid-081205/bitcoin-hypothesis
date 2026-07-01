"""Bitcoin Hypothesis: regression & correlation analysis on real data.

Reads the CSVs produced by fetch_data.py and answers, with actual numbers:
  1. What macro factors explain BTC returns? (multi-factor OLS, weekly, HAC errors)
  2. How has BTC's correlation with equities / gold / dollar / rates evolved?
  3. Does sentiment (Fear & Greed) drive price, or is it contrarian?
  4. How sensitive is BTC to interest-rate moves, and did that change post-ETF?
  5. Does money supply (M2) growth matter?
  6. How does the current drawdown compare structurally to 2018 and 2022?
  7. What did discrete government / structural events actually do to price?

Outputs: site/data.json (everything the website needs) + analysis/results.md
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT_JSON = ROOT / "docs" / "data.json"
OUT_MD = ROOT / "analysis" / "results.md"


def load():
    def csv(name, **kw):
        return pd.read_csv(DATA / f"{name}.csv", parse_dates=["date"], **kw).set_index("date")

    d = {}
    for name in ["btc", "sp500", "nasdaq", "gold", "dxy"]:
        d[name] = csv(name)["close"].rename(name)
    for name in ["fed_funds", "treasury_10y", "m2", "cpi", "hash_rate", "active_addresses"]:
        d[name] = csv(name)["value"].rename(name)
    fg = csv("fear_greed")
    fg.index = fg.index.normalize()
    d["fear_greed"] = fg["value"].rename("fear_greed")
    return d


def build_daily(d):
    df = pd.concat(
        [d[k] for k in ["btc", "sp500", "nasdaq", "gold", "dxy", "fed_funds", "treasury_10y", "fear_greed"]],
        axis=1,
    ).sort_index()
    # macro series only print on business days; forward-fill over weekends
    for col in ["sp500", "nasdaq", "gold", "dxy", "fed_funds", "treasury_10y"]:
        df[col] = df[col].ffill()
    return df[df["btc"].notna()]


def weekly_factor_regression(daily, start=None, end=None):
    """BTC weekly log return ~ nasdaq + gold + dxy + change in 10y + change in F&G."""
    df = daily.copy()
    if start:
        df = df[df.index >= start]
    if end:
        df = df[df.index <= end]
    w = df.resample("W-FRI").last()
    y = np.log(w["btc"]).diff()
    X = pd.DataFrame(
        {
            "nasdaq_ret": np.log(w["nasdaq"]).diff(),
            "gold_ret": np.log(w["gold"]).diff(),
            "dxy_ret": np.log(w["dxy"]).diff(),
            "d_10y": w["treasury_10y"].diff(),
            "d_fear_greed": w["fear_greed"].diff() / 100.0,
        }
    )
    m = pd.concat([y.rename("btc_ret"), X], axis=1).dropna()
    model = sm.OLS(m["btc_ret"], sm.add_constant(m[X.columns])).fit(
        cov_type="HAC", cov_kwds={"maxlags": 4}
    )
    return model, len(m)


def reg_to_dict(model, n, label):
    rows = []
    for name in model.params.index:
        rows.append(
            {
                "var": name,
                "coef": round(float(model.params[name]), 4),
                "t": round(float(model.tvalues[name]), 2),
                "p": round(float(model.pvalues[name]), 4),
            }
        )
    return {"label": label, "n": n, "r2": round(float(model.rsquared), 3), "coefs": rows}


def rolling_correlations(daily):
    rets = np.log(daily[["btc", "nasdaq", "gold", "dxy"]]).diff()
    rets["d_10y"] = daily["treasury_10y"].diff()
    out = {}
    for col in ["nasdaq", "gold", "dxy", "d_10y"]:
        rc = rets["btc"].rolling(90).corr(rets[col]).resample("W-FRI").last().dropna()
        out[col] = [{"d": i.strftime("%Y-%m-%d"), "v": round(float(v), 3)} for i, v in rc.items()]
    return out


def sentiment_analysis(daily):
    """Forward 30d BTC return conditioned on Fear & Greed quintile (contrarian test)."""
    df = daily[["btc", "fear_greed"]].dropna().copy()
    df["fwd30"] = df["btc"].shift(-30) / df["btc"] - 1
    df = df.dropna()
    bins = [0, 20, 40, 60, 80, 101]
    labels = ["Extreme Fear (0-20)", "Fear (20-40)", "Neutral (40-60)", "Greed (60-80)", "Extreme Greed (80-100)"]
    df["bucket"] = pd.cut(df["fear_greed"], bins=bins, labels=labels, right=False)
    g = df.groupby("bucket", observed=True)["fwd30"]
    table = [
        {
            "bucket": str(k),
            "mean_fwd30": round(float(v.mean()) * 100, 2),
            "median_fwd30": round(float(v.median()) * 100, 2),
            "hit_rate_pos": round(float((v > 0).mean()) * 100, 1),
            "n": int(v.count()),
        }
        for k, v in g
    ]
    # does sentiment lead price, or price lead sentiment? cross-correlation of changes
    dfg = df["fear_greed"].diff()
    dbtc = np.log(df["btc"]).diff()
    lead_lag = []
    for lag in range(-10, 11):
        c = dbtc.corr(dfg.shift(lag))
        lead_lag.append({"lag": lag, "corr": round(float(c), 3)})
    current = daily["fear_greed"].dropna()
    return {
        "quintiles": table,
        "lead_lag": lead_lag,
        "current": int(current.iloc[-1]),
        "current_date": current.index[-1].strftime("%Y-%m-%d"),
        "series": [
            {"d": i.strftime("%Y-%m-%d"), "v": int(v)}
            for i, v in current.resample("W-FRI").last().dropna().items()
        ],
    }


def rate_sensitivity(daily):
    """BTC daily return on large 10y-yield move days, split by era."""
    df = daily[["btc", "treasury_10y"]].copy()
    df["btc_ret"] = np.log(df["btc"]).diff()
    df["d10"] = df["treasury_10y"].diff()
    df = df.dropna()
    eras = {
        "2014-2019 (pre-institutional)": ("2014-01-01", "2019-12-31"),
        "2020-2023 (covid / QE / tightening)": ("2020-01-01", "2023-12-31"),
        "2024-2026 (ETF era)": ("2024-01-01", "2026-12-31"),
    }
    rows = []
    for label, (a, b) in eras.items():
        s = df[(df.index >= a) & (df.index <= b)]
        big_up = s[s["d10"] >= 0.05]["btc_ret"]
        big_dn = s[s["d10"] <= -0.05]["btc_ret"]
        beta = sm.OLS(s["btc_ret"], sm.add_constant(s["d10"])).fit()
        rows.append(
            {
                "era": label,
                "beta_per_10bp": round(float(beta.params["d10"]) * 0.10 * 100, 2),
                "t": round(float(beta.tvalues["d10"]), 2),
                "avg_ret_yield_spike": round(float(big_up.mean()) * 100, 2),
                "avg_ret_yield_drop": round(float(big_dn.mean()) * 100, 2),
                "n_spike_days": int(len(big_up)),
            }
        )
    return rows


def m2_analysis(d):
    m2 = d["m2"].resample("MS").last()
    btc_m = d["btc"].resample("MS").last()
    df = pd.concat([btc_m, m2], axis=1).dropna()
    df["btc_yoy"] = df["btc"].pct_change(12) * 100
    df["m2_yoy"] = df["m2"].pct_change(12) * 100
    df = df.dropna()
    best = None
    for lag in range(0, 13):
        c = df["btc_yoy"].corr(df["m2_yoy"].shift(lag))
        if best is None or abs(c) > abs(best["corr"]):
            best = {"lag": lag, "corr": round(float(c), 3)}
    return {
        "contemporaneous_corr": round(float(df["btc_yoy"].corr(df["m2_yoy"])), 3),
        "best_lag": best,
        "series": [
            {"d": i.strftime("%Y-%m"), "btc_yoy": round(float(r["btc_yoy"]), 1), "m2_yoy": round(float(r["m2_yoy"]), 2)}
            for i, r in df.iterrows()
        ],
    }


def cycle_drawdowns(btc):
    """Align the three big bears from their ATHs: 2017-12, 2021-11, 2025-10."""
    tops = {"2018 bear": "2017-12-16", "2022 bear": "2021-11-08", "2026 bear (current)": "2025-10-06"}
    out = {}
    for label, top in tops.items():
        s = btc[btc.index >= top].iloc[:730]
        norm = s / s.iloc[0] * 100
        ds = norm.iloc[::7]
        out[label] = [{"day": int((i - s.index[0]).days), "v": round(float(v), 1)} for i, v in ds.items()]
    dd = (btc / btc.cummax() - 1) * 100
    dd_w = dd.resample("W-FRI").last().dropna()
    return {
        "aligned": out,
        "drawdown_series": [{"d": i.strftime("%Y-%m-%d"), "v": round(float(v), 1)} for i, v in dd_w.items()],
        "current_drawdown": round(float(dd.iloc[-1]), 1),
    }


EVENTS = [
    {"date": "2017-09-04", "label": "China bans ICOs & exchanges", "type": "government"},
    {"date": "2020-03-12", "label": "COVID liquidity crash", "type": "macro"},
    {"date": "2021-05-19", "label": "China mining ban escalation", "type": "government"},
    {"date": "2021-09-24", "label": "China declares all crypto tx illegal", "type": "government"},
    {"date": "2022-05-09", "label": "Terra/LUNA collapse", "type": "structural"},
    {"date": "2022-11-08", "label": "FTX collapse", "type": "structural"},
    {"date": "2023-03-10", "label": "SVB failure / banking stress", "type": "macro"},
    {"date": "2024-01-10", "label": "US spot ETF approval", "type": "government"},
    {"date": "2024-04-19", "label": "4th halving", "type": "structural"},
    {"date": "2024-11-05", "label": "US election (pro-crypto shift)", "type": "government"},
    {"date": "2025-10-10", "label": "Tariff shock: $19B liquidation", "type": "government"},
    {"date": "2026-06-02", "label": "Strategy discloses BTC sale", "type": "structural"},
]


def event_study(btc):
    rows = []
    for ev in EVENTS:
        t0 = pd.Timestamp(ev["date"])
        idx = btc.index.searchsorted(t0)
        if idx < 5 or idx + 30 >= len(btc):
            window_end = min(idx + 30, len(btc) - 1)
        else:
            window_end = idx + 30
        p_pre = float(btc.iloc[idx - 1])
        p_7 = float(btc.iloc[min(idx + 7, len(btc) - 1)])
        p_30 = float(btc.iloc[window_end])
        rows.append(
            {
                **ev,
                "ret_7d": round((p_7 / p_pre - 1) * 100, 1),
                "ret_30d": round((p_30 / p_pre - 1) * 100, 1),
            }
        )
    return rows


def price_and_valuation(btc, d):
    wma200 = btc.rolling(1400).mean()  # 200 weeks = 1400 days
    mayer = btc / btc.rolling(200).mean()
    w = pd.concat([btc.rename("p"), wma200.rename("wma"), mayer.rename("mayer")], axis=1).resample("W-FRI").last()
    hash_rate = d["hash_rate"]
    hr_w = hash_rate.resample("W-FRI").last().dropna()
    return {
        "price_series": [
            {"d": i.strftime("%Y-%m-%d"), "p": round(float(r["p"]), 0), "wma": (round(float(r["wma"]), 0) if pd.notna(r["wma"]) else None)}
            for i, r in w.iterrows()
            if pd.notna(r["p"])
        ],
        "mayer_current": round(float(mayer.dropna().iloc[-1]), 2),
        "price_vs_200wma": round(float(btc.iloc[-1] / wma200.dropna().iloc[-1] - 1) * 100, 1),
        "hash_rate": [
            {"d": i.strftime("%Y-%m-%d"), "v": round(float(v) / 1e6, 1)} for i, v in hr_w.items()  # EH/s
        ],
        "hash_rate_ath_ratio": round(float(hash_rate.iloc[-1] / hash_rate.max()), 3),
    }


def snapshot(daily, d):
    btc = daily["btc"]
    last = btc.index[-1]
    ath = btc.max()
    ret = lambda days: round(float(btc.iloc[-1] / btc.iloc[-1 - days] - 1) * 100, 1)
    return {
        "as_of": last.strftime("%Y-%m-%d"),
        "price": round(float(btc.iloc[-1]), 0),
        "ath": round(float(ath), 0),
        "ath_date": btc.idxmax().strftime("%Y-%m-%d"),
        "from_ath_pct": round(float(btc.iloc[-1] / ath - 1) * 100, 1),
        "ret_30d": ret(30),
        "ret_90d": ret(90),
        "ret_365d": ret(365),
        "fed_funds": round(float(daily["fed_funds"].dropna().iloc[-1]), 2),
        "treasury_10y": round(float(daily["treasury_10y"].dropna().iloc[-1]), 2),
        "dxy": round(float(daily["dxy"].dropna().iloc[-1]), 1),
        "vol_90d_ann": round(float(np.log(btc).diff().tail(90).std() * np.sqrt(365) * 100), 1),
    }


def main():
    d = load()
    daily = build_daily(d)
    btc = daily["btc"]

    full_model, n_full = weekly_factor_regression(daily)
    pre_model, n_pre = weekly_factor_regression(daily, end="2023-12-31")
    etf_model, n_etf = weekly_factor_regression(daily, start="2024-01-01")

    results = {
        "generated": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "snapshot": snapshot(daily, d),
        "regressions": [
            reg_to_dict(full_model, n_full, "Full sample (2018-2026, weekly)"),
            reg_to_dict(pre_model, n_pre, "Pre-ETF era (2018-2023)"),
            reg_to_dict(etf_model, n_etf, "ETF era (2024-2026)"),
        ],
        "rolling_corr": rolling_correlations(daily),
        "sentiment": sentiment_analysis(daily),
        "rate_sensitivity": rate_sensitivity(daily),
        "m2": m2_analysis(d),
        "cycles": cycle_drawdowns(btc),
        "events": event_study(btc),
        "valuation": price_and_valuation(btc, d),
    }

    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(results, indent=1))
    # also emit data.js so the site works over file:// without a server
    (OUT_JSON.parent / "data.js").write_text("window.DATA = " + json.dumps(results) + ";")
    print(f"wrote {OUT_JSON} ({OUT_JSON.stat().st_size // 1024} KB)")

    # console summary
    print("\n=== SNAPSHOT ===")
    print(json.dumps(results["snapshot"], indent=2))
    print("\n=== FACTOR REGRESSIONS (weekly BTC log returns) ===")
    for reg in results["regressions"]:
        print(f"\n{reg['label']}  n={reg['n']}  R2={reg['r2']}")
        for c in reg["coefs"]:
            print(f"  {c['var']:>14}: coef={c['coef']:>8}  t={c['t']:>6}  p={c['p']}")
    print("\n=== SENTIMENT QUINTILES (fwd 30d return) ===")
    for q in results["sentiment"]["quintiles"]:
        print(f"  {q['bucket']:>24}: mean={q['mean_fwd30']:>6}%  median={q['median_fwd30']:>6}%  hit={q['hit_rate_pos']}%  n={q['n']}")
    print("\n=== RATE SENSITIVITY BY ERA ===")
    for r in results["rate_sensitivity"]:
        print(f"  {r['era']}: beta/10bp={r['beta_per_10bp']}%  t={r['t']}  spike-day avg={r['avg_ret_yield_spike']}%")
    print("\n=== M2 ===")
    print(f"  contemporaneous corr={results['m2']['contemporaneous_corr']}  best lag={results['m2']['best_lag']}")
    print("\n=== EVENTS ===")
    for e in results["events"]:
        print(f"  {e['date']} {e['label']:<40} 7d={e['ret_7d']:>6}%  30d={e['ret_30d']:>6}%")
    print("\n=== CYCLES ===")
    print(f"  current drawdown: {results['cycles']['current_drawdown']}%")
    print(f"  mayer multiple: {results['valuation']['mayer_current']}, price vs 200WMA: {results['valuation']['price_vs_200wma']}%")


if __name__ == "__main__":
    main()
