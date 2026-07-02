# bitcoin hypothesis

what actually moves bitcoin's price. real data, real regressions, no vibes.

btc is −52% from the oct 2025 ath. everyone has an opinion. this repo has 4,300 days of price data, 10k nlp-scored headlines, and OLS with newey-west errors instead.

**live site →** https://sid-081205.github.io/bitcoin-hypothesis/

## the stack

```
scripts/fetch_data.py           # prices, rates, m2, fear&greed, hash rate. no api keys.
scripts/fetch_nlp_sentiment.py  # ~10k headlines scored with vader + crypto lexicon
scripts/run_analysis.py         # regressions, event studies, cycle math -> docs/data.json
data/                           # raw csvs, committed. reproduce everything.
analysis/results.md             # the written findings
analysis/decisions.md           # dated decision journal. auditable reasoning chain.
UPDATE_PLAYBOOK.md              # standing instructions for re-running the whole thing
docs/                           # the site. static html + chart.js, served by gh pages
```

## what the numbers say

- bitcoin is a leveraged tech stock. nasdaq beta ~0.5, the only factor that survives every era. it went *up* after the etfs arrived. "digital gold" beta: statistically zero.
- sentiment doesn't drive price. price drives sentiment (corr 0.57 with *tomorrow's* sentiment, ~0 the other way). the news is a mirror.
- extreme fear has paid +5.0% fwd 30d, 63% hit rate. we're at 11/100.
- rates matter by regime, not by tick. both post-2020 bears are hawkish-repricing years.
- m2 charts are a meme. corr 0.17.
- governments have never killed it. china's third ban: +36% in 30 days.
- this bear is flow-driven — $19b liquidation cascade, record etf outflows, hawkish fed. nothing structural broke. hash rate still 78% of ath.

## run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/fetch_data.py
.venv/bin/python scripts/run_analysis.py
open docs/index.html
```

## disclaimer

research, not financial advice. every number is computed from the committed raw data. past performance predicts nothing.
