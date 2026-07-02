# Update Playbook

This file is the standing instruction set for refreshing the Bitcoin Hypothesis analysis.
When the user says something like **"run the analysis"**, **"update the thesis"**, or
**"what should I do now?"** — follow these steps in order. The goal is a new, dated,
auditable decision that explicitly builds on the previous ones.

## Step 1 — Refresh all real data

```bash
cd ~/bitcoin-hypothesis
.venv/bin/python scripts/fetch_data.py           # prices, rates, F&G, on-chain
.venv/bin/python scripts/fetch_nlp_sentiment.py  # ~2 min; re-scores news headlines
.venv/bin/python scripts/run_analysis.py         # recomputes everything -> docs/data.json + data.js
```

Sanity-check the console output: snapshot date must be within 2 days of today; no empty datasets.

## Step 2 — Gather real market news

Web-search (adjust dates to today):

1. "bitcoin price news this week" — what moved and why
2. "bitcoin ETF flows this week" — is the marginal buyer still selling? (the #1 signal)
3. "Fed rate expectations" — hawkish or dovish repricing?
4. "bitcoin regulation news" — any government/legislative catalyst
5. Anything structural: exchange/stablecoin/custodian/treasury-company stress

## Step 3 — Read the past thought processes

Read `analysis/decisions.md` — at minimum the two most recent entries. Note:
- the stance and its stated triggers,
- which triggers have since fired or expired,
- any prediction made that can now be scored right or wrong (score it honestly).

## Step 4 — Evaluate the signal checklist

From the fresh `docs/data.json` and the news, set each signal green/amber/red:

| Signal | Green when | Red when |
|---|---|---|
| Price vs 200WMA | at or below | >25% above |
| Fear & Greed | ≤20 | ≥80 |
| NLP press tone percentile | ≤15th | ≥85th |
| ETF flows (from news) | net inflows 2-3 wks | record/streak outflows |
| Fed direction (from news) | dovish repricing | hawkish repricing |
| Network health (hash rate vs ATH) | ≥60% | <40% or falling fast |
| Cycle position vs 2018/2022 template | past month 12 + deep drawdown | early in decline |

Stances: **ADD AGGRESSIVELY** (most green, a trigger fired) · **STAGED ACCUMULATION**
(valuation green, flows/macro red) · **HOLD / WAIT** (mixed, deteriorating) ·
**REDUCE / STOP** (structural failure signal).

## Step 5 — Write the new decision entry

Append a new entry at the TOP of `analysis/decisions.md` (keep the format of entry #1):
data snapshot, what the news said (with real numbers), the decision, triggers, and —
mandatory — **"Reasoning vs prior entry"**: what changed since last time, which prior
predictions were right/wrong, and why the stance did or didn't move.

## Step 6 — Update the website

1. Update `docs/verdict.json`: `updated`, `price_at_analysis`, `stance`, `one_liner`,
   the `signals` array, `next_triggers`, and APPEND (never overwrite) to `history`.
2. The live page (`docs/live.html`) reads `verdict.json` and `data.js` automatically — no edit needed.
3. If headline findings changed materially, update the affected prose in `docs/index.html`,
   `analysis/results.md`, and the two case pages.

## Step 7 — Verify before pushing

```bash
# script executes clean and all charts construct
node -e "const fs=require('fs');const html=fs.readFileSync('docs/index.html','utf8');const s=html.split('<script>').pop().split('</script>')[0];global.window={};require('./docs/data.js');let n=0;global.Chart=class{constructor(){n++}};global.Chart.defaults={font:{},plugins:{legend:{labels:{}}}};global.document={getElementById:()=>({set innerHTML(v){},set textContent(v){}}),documentElement:{}};global.getComputedStyle=()=>({getPropertyValue:()=>'m'});eval(s);console.log('ok',n,'charts')"
# verdict.json is valid
node -e "JSON.parse(require('fs').readFileSync('docs/verdict.json'))" && echo "verdict ok"
```

Also spot-check that any number quoted in prose matches `docs/data.json` (the narrative
must never drift from the computed data).

## Step 8 — Ship

```bash
git add -A && git commit -m "Analysis update YYYY-MM-DD: <stance> — <one-line reason>" && git push
```

Wait ~60s for the Pages build, then confirm the live site serves the new `verdict.json`
(`curl -s https://sid-081205.github.io/bitcoin-hypothesis/verdict.json | head`).

## Step 9 — Report to the user

Lead with the stance and whether it changed. Then: which triggers fired, what the key
numbers are now vs last entry, and what would change the stance next. Keep it short;
link to the live page.
