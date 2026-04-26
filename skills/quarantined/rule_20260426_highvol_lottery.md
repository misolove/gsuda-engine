---
rule_id: rule_20260426_highvol_lottery
status: quarantined
description: Candidate suppression rule for Buy signals with elevated 20-day 
  volatility, generated from clustered failed trades.
trigger_conditions:
- feature: signal
  op: '='
  value: Buy
- feature: volatility_20
  op: '>='
  value: 2.0
action:
  type: suppress_trade
  reason: High-volatility Buy setup matched a failure cluster and requires 
    empirical validation before deployment.
spawned_from_cluster:
  cluster_id: highvol_lottery
  failure_count: 36
  avg_failed_return_pct: -6.5823
  worst_return_pct: -11.9101
spawned_from_failures:
- trade_highvol_000
- trade_highvol_001
- trade_highvol_002
- trade_highvol_005
- trade_highvol_006
- trade_highvol_007
- trade_highvol_010
- trade_highvol_011
- trade_highvol_012
- trade_highvol_015
- trade_highvol_016
- trade_highvol_017
- trade_highvol_020
- trade_highvol_021
- trade_highvol_022
- trade_highvol_025
- trade_highvol_026
- trade_highvol_027
- trade_highvol_030
- trade_highvol_031
sample_evidence:
- trade_id: trade_highvol_000
  return_pct: -11.2455
  sector: 전기제품
  month_pillar: 庚辰
  jieqi_zone: first_3
  volatility_20: 2.9124
- trade_id: trade_highvol_001
  return_pct: -9.2562
  sector: 소프트웨어
  month_pillar: 壬申
  jieqi_zone: middle
  volatility_20: 3.2445
- trade_id: trade_highvol_002
  return_pct: -8.6611
  sector: 2차전지
  month_pillar: 甲戌
  jieqi_zone: last_3
  volatility_20: 2.2378
- trade_id: trade_highvol_005
  return_pct: -10.6871
  sector: 소프트웨어
  month_pillar: 甲戌
  jieqi_zone: last_3
  volatility_20: 3.397
- trade_id: trade_highvol_006
  return_pct: -1.7532
  sector: 2차전지
  month_pillar: 庚辰
  jieqi_zone: first_3
  volatility_20: 2.7291
backtest_stats:
  historical_matches: 60
  cluster_precision: 0.6
  winner_damage_pct: 40.0
  avg_return_pct: 0.4075
  median_return_pct: -3.0097
  oos_matches: 40
  oos_precision: 0.6
  oos_avg_return_pct: -0.1585
  oos_median_return_pct: -3.1537
  oos_2024_2025_holds: true
deployment_gate:
  requires_backtest: true
  auto_deploy: false
notes:
- This rule is a conservative candidate only and must not be activated until the
  validator replaces placeholder stats.
- Saju/Yi-derived fields in the evidence are treated as domain-informed 
  categorical features, not as claims that Saju predicts stock prices.
failure_reason: winner_damage_gt_35pct
---

## Why this rule exists

This candidate was spawned from the `highvol_lottery` failed-trade cluster, which contains Buy recommendations with elevated `volatility_20`. The cluster summary reports 36 failures, an average failed return of `-6.5823%`, and a worst return of `-11.9101%`.

The cluster rationale notes that this is a tempting high-volatility suppression but may cause winner damage, so it must remain a candidate until empirical validation is complete.

## What it does

When a trade recommendation has:

- `signal = Buy`
- `volatility_20 >= 2.0`

the rule proposes suppressing the trade before execution.

This rule does not claim that volatility, Saju/Yi categories, month pillars, or solar-term features predict prices by themselves. It only records a provenance-linked hypothesis generated from failed trades. The validator must test historical match quality, cluster precision, winner damage, and 2024-2025 out-of-sample performance before this rule can move to active deployment.