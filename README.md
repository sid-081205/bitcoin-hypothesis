# Bitcoin Hypothesis

A data-driven investigation into what actually moves Bitcoin's price — and whether it is worth an investment during the current drawdown (−52% from the October 2025 all-time high as of July 2026).

**Live site:** https://sid-081205.github.io/bitcoin-hypothesis/

## What's in here

| Path | What it is |
|---|---|
| `scripts/fetch_data.py` | Pulls all raw data: BTC + macro prices (Yahoo Finance), rates/M2/CPI (FRED), Fear & Greed (alternative.me), hash rate & addresses (blockchain.info). No API keys needed. |
| `scripts/run_analysis.py` | All statistics: multi-factor OLS regressions (HAC errors), rolling correlations, sentiment conditioning, rate-sensitivity by era, M2 lead-lag, event studies, cycle-aligned drawdowns. Emits `docs/data.json` / `docs/data.js`. |
| `data/` | The raw CSVs, committed for reproducibility. |
| `analysis/results.md` | The written research findings. |
| `docs/` | The static website (GitHub Pages). One HTML file + Chart.js + the computed data. |

## Headline findings

1. **Bitcoin trades as a high-beta tech-risk asset.** NASDAQ beta ≈ 0.5 is the only consistently significant macro factor, and it *rose* in the ETF era (R² 0.34 → 0.42). The "digital gold" beta is statistically zero and turned negative post-2024.
2. **Sentiment mirrors price rather than driving it.** Price today correlates 0.57 with *tomorrow's* sentiment change; the reverse is ~0. As a signal, extreme fear (current reading: 11) has averaged +5.0% forward 30-day returns with a 63% hit rate.
3. **Rates matter through regime, not ticks.** Daily yield-change betas are insignificant in every era, but both post-2020 bear markets (2022, 2026) are hawkish-repricing years.
4. **M2 is a weak explanation.** BTC YoY vs M2 YoY correlates at 0.17 (0.24 at a 7-month lag).
5. **Governments have never been fatal.** Hostile actions produced single-digit-to-teens drawdowns with decaying impact (China's third ban: +36% in the following 30 days). The largest positive events were favorable US policy shifts — which also makes the current stalled legislation a real drag.
6. **The current bear is flow-driven:** the Oct 10 2025 liquidation cascade ($19B), record spot-ETF outflows, treasury-company unwinds, and a hawkish Fed — not a protocol or credibility failure.

## Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/fetch_data.py    # refresh raw data
.venv/bin/python scripts/run_analysis.py  # recompute everything
open docs/index.html                      # view the site
```

## Disclaimer

This is research, not financial advice. All statistics are computed from the committed raw data; past performance does not predict future results.
