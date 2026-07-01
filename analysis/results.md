# Bitcoin Hypothesis — Research Findings

*Data through 2026-07-01. All numbers computed from raw data in `/data` by `scripts/run_analysis.py`. Sources: Yahoo Finance, FRED, alternative.me, blockchain.info. Nothing here is financial advice.*

## 1. Where we are

- **Price:** ~$60,357 (2026-07-01), **−51.6% from the all-time high** of $124,753 set 2025-10-06.
- Returns: −15.4% (30d), −9.8% (90d), −42.9% (1y). June 2026 was the worst month since June 2022.
- Macro backdrop: fed funds 3.63%, 10Y treasury 4.44%, DXY 101.4 (strong dollar), and market pricing has flipped toward **rate hikes**, not cuts.
- Fear & Greed index: **11 (extreme fear)**.
- Realized volatility (90d, annualized): 37.5% — low by Bitcoin standards, consistent with a grind-down rather than a panic.

## 2. Fundamental history: what drove Bitcoin, cycle by cycle

**2014–2016 (post-Mt.Gox winter).** Retail-only market. Price driven by exchange failures and slow adoption recovery. No meaningful macro correlation — our regressions show near-zero NASDAQ beta and zero rate sensitivity in this era.

**2017–2018 (ICO bubble).** Retail speculation and the ICO boom drove BTC from ~$1k to ~$19.7k, then an −84% bear as the bubble unwound. China's Sept 2017 exchange/ICO ban knocked ~9% off in a week but did not end the rally — the top came three months later from exhaustion, not regulation.

**2020–2021 (liquidity cycle).** COVID QE, zero rates, and the first institutional wave (MicroStrategy, Tesla, Coinbase IPO) took BTC to ~$69k. This is when the "macro asset" era began: our rolling 90-day correlation with NASDAQ, roughly zero pre-2020, jumped above 0.4 and has never durably returned to zero since.

**2022 (tightening + structural collapses).** The Fed's fastest hiking cycle in 40 years repriced all risk assets, and crypto-native leverage imploded on top of it: Terra/LUNA (−12% in 7d), then FTX (−18% in 7d, −77% peak-to-trough for the cycle). Note both structural collapses did far more measurable damage than any government action in our event study.

**2023–2025 (the ETF era).** SVB banking stress in March 2023 was Bitcoin's single best 30-day event window in our study (+39%) — the "alternative to banks" narrative got a live demo. US spot ETF approval (Jan 2024) was a sell-the-news event short-term (−7.4% in 7d) but structurally rerouted institutional flows. The April 2024 halving, the Nov 2024 pro-crypto election result (+42% in 30d — the largest positive event response we measured), and record ETF inflows carried BTC to $126k by October 2025.

**October 2025 → now (the current fall).** The reversal has three layers:

1. **The trigger (2025-10-10):** a surprise 100% China-tariff announcement hit a market carrying record ~$217B of open interest on a Friday evening. ~$19B in leveraged positions were liquidated — roughly 9× the previous single-day record — and order-book depth collapsed and never fully recovered.
2. **The bid disappeared:** spot ETFs, the marginal buyer of 2024–25, flipped to record outflows (~$3.3B out in H1 2026, including an $818M single day in January and a record 13-day outflow streak in June). Corporate-treasury confidence broke when Strategy disclosed selling BTC (June 2026: −13.6% in 7d).
3. **Macro turned hostile:** hawkish Fed repricing (futures went from ~23% to ~64% odds of hikes by September in one month), a strong dollar, and capital rotating into AI equities — which posted their best quarter in years while crypto fell.

Result: two consecutive losing quarters (−22%, −14%) to start the year — a pattern seen before only in 2018 and 2022, both structural bear markets.

## 3. What the regressions actually say

Weekly BTC log returns regressed on NASDAQ return, gold return, DXY return, Δ10Y yield, and ΔFear&Greed (OLS, HAC/Newey-West errors):

| | Full 2018–26 (n=439) | Pre-ETF 2018–23 (n=309) | ETF era 2024–26 (n=130) |
|---|---|---|---|
| NASDAQ beta | **0.47 (t=3.6)** | **0.47 (t=2.8)** | **0.50 (t=3.0)** |
| Gold beta | 0.25 (n.s.) | 0.63 (t=1.9, marginal) | −0.12 (n.s.) |
| DXY beta | −0.65 (n.s.) | −0.39 (n.s.) | −0.63 (n.s.) |
| Δ10Y yield | 0.05 (n.s.) | 0.07 (marginal) | 0.02 (n.s.) |
| ΔF&G /100 | **0.34 (t=10.8)** | **0.37 (t=8.4)** | **0.27 (t=9.8)** |
| R² | 0.34 | 0.34 | 0.42 |

**Reading:**

- **Bitcoin trades like a leveraged tech-risk asset.** The NASDAQ beta of ~0.5 is the only macro factor that is consistently, strongly significant, and it *rose* slightly in the ETF era. R² increased from 0.34 to 0.42 post-ETF: institutionalization made BTC *more* macro-driven, not less.
- **The "digital gold" claim fails in-sample.** The gold beta was marginally positive pre-2024 and is now slightly *negative*. In the current stress, gold and BTC fell together against a strong dollar.
- **Interest rates matter through regime, not ticks.** Daily/weekly yield-change betas are statistically insignificant in every era (|t| < 2). But the era splits tell the real story: rate sensitivity is about the *level and direction of the cycle* (2022 and 2026, the two worst years, are both hawkish-repricing years), transmitted via risk appetite and the dollar rather than via day-to-day yield moves.
- **Sentiment is a mirror, not a driver.** ΔF&G is the strongest regressor contemporaneously, but the lead-lag analysis shows causality runs from price to sentiment: today's BTC return correlates 0.57 with *tomorrow's* sentiment change, and only 0.01 the other way. "Bad sentiment" is not causing the fall — it's recording it.

## 4. Sentiment as a signal (contrarian test)

Forward 30-day return conditioned on the Fear & Greed level (2018–2026):

| F&G bucket | Mean fwd 30d | Hit rate | n |
|---|---|---|---|
| Extreme Fear (0–20) | **+5.0%** | 62.9% | 326 |
| Fear (20–40) | −0.5% | 45.6% | 968 |
| Neutral (40–60) | +3.7% | 54.6% | 806 |
| Greed (60–80) | +5.0% | 52.3% | 774 |
| Extreme Greed (80–100) | +19.9% | 72.1% | 165 |

Two honest observations: extreme fear (where we are now, at 11) has historically been a *mildly* positive contrarian entry — but the best historical bucket was actually extreme greed, i.e. momentum. The distribution is U-shaped, not simply contrarian. The worst zone is ordinary fear (20–40), which is where slow bleeds live.

## 4b. NLP cross-reference: reading the news itself

The Fear & Greed index is computed from market data (volatility, volume, dominance) and never reads text. As an independent check we scored **10,358 Bitcoin-related headlines** (Hacker News archive, 2018–2026) with VADER — a lexicon + rule-based NLP sentiment model — extended with a finance/crypto vocabulary (crash, liquidation, bullish, ETF outflows, etc.), aggregated monthly.

- **The two sentiment measures agree without sharing inputs:** monthly correlation of NLP press tone with F&G is **0.38** — decent convergent validity for two entirely different methodologies.
- **Text confirms the mirror finding:** press tone correlates **0.31** with the *same* month's BTC return but only **0.04** with the *next* month's. Journalists describe what price already did; coverage tone has essentially zero predictive power.
- **Current reading is historically extreme:** June 2026 tone was **−0.088, the 7.8th percentile** of all 102 months — among the most negative Bitcoin coverage on record. 34% of headlines scored negative vs 9% positive.
- **Contrarian tercile test:** months in the most-negative-press tercile were followed by **+7.1%** mean next-month returns (62% hit rate); neutral-press months were the worst (−2.2%). Same U-shape as the F&G quintiles: maximum pessimism in text has been a mild buy signal, not a sell signal.

## 5. Money supply

The popular "BTC follows M2" thesis is weak in US data: YoY BTC returns vs YoY M2 growth correlate at just **0.17** contemporaneously, peaking at **0.24 with a 7-month lag**. Liquidity matters directionally (2020–21 vs 2022 is the cleanest evidence) but M2 alone explains very little variance and is not a usable timing tool.

## 6. Government actions: measured, not imagined

Event-study returns around discrete government/regulatory events:

| Event | 7d | 30d |
|---|---|---|
| China ICO/exchange ban (2017) | −9.2% | −7.7% |
| China mining ban (May 2021) | −8.4% | −16.6% |
| China "all crypto illegal" (Sep 2021) | +7.2% | **+35.7%** |
| US spot ETF approval (Jan 2024) | −7.4% | +2.2% |
| US election, pro-crypto (Nov 2024) | +29.7% | **+42.4%** |
| Tariff shock (Oct 2025) | −12.5% | −14.0% |

Hostile government actions have consistently produced single-digit-to-teens drawdowns that the market absorbed — by China's third ban the market ignored it entirely. The largest *positive* event in the whole study was a favorable US policy shift. The conclusion cuts both ways: government hostility has never killed Bitcoin, but the 2024–25 rally was unusually dependent on policy goodwill, which makes stalled US crypto legislation a live drag now. The Oct 2025 tariff shock also shows the new failure mode: it hurt not as crypto policy but as a *macro risk event* hitting a leveraged market.

## 7. Survival indicators

- **Hash rate** is at 78% of its all-time high — down with price economics but historically extreme resilience; the security budget is intact.
- **Price sits 3.4% below the 200-week moving average** (Mayer multiple 0.80). Every prior touch of the 200WMA (2015, 2018, 2020, 2022) marked the bottom third of the cycle. In 2018 and 2022, price fell a further ~15–25% *below* the 200WMA before bottoming.
- **Drawdown depth:** −51.6% now, vs −84% (2018) and −77% (2022) at their troughs. Aligned from ATH, the current path (day ~266) is tracking *between* the 2018 and 2022 trajectories — deeper than a correction, shallower so far than prior full bears.

## 8. The investment verdict

**Bear case (what the data says is real):** the marginal buyer (ETFs) is a seller; the Fed is repricing hawkish and BTC has never bottomed during a hawkish repricing; the institutionalization trade raised NASDAQ beta so BTC no longer diversifies; the two-losing-quarters pattern has only occurred in structural bears; liquidity depth is impaired since Oct-10; and prediction markets price a ~52% chance of sub-$50k this year.

**Bull case (equally real):** price is at the 200WMA, historically the single best accumulation zone across four cycles; sentiment at 11 is in the historically positive contrarian bucket (+5% mean fwd 30d, 63% hit rate); hash rate confirms no network-level stress; every prior "Bitcoin is dead" drawdown of ≥50% eventually resolved to new highs; and the sell pressure is flow-driven (ETF redemptions, treasury unwinds) rather than a protocol or credibility failure — historically the recoverable kind.

**Synthesis.** The honest statistical answer is that Bitcoin's price is currently ~40–50% explained by two things you can watch: tech-equity risk appetite and its own reflexive sentiment. Neither has turned. Valuation (200WMA, Mayer 0.80) says the risk/reward for a multi-year holder is better than at almost any point since late 2022, but both prior analogs bottomed only *after* the macro cycle turned (2018: Fed pivot Jan 2019; 2022: peak inflation + pivot hopes). A rational structure implied by this data: this is a staged-accumulation zone for capital with a multi-year horizon and tolerance for a further −20–30% leg, not a momentum entry — and the single most informative catalyst to watch is ETF flows turning, because the entire 2024–25 repricing was built on them.
