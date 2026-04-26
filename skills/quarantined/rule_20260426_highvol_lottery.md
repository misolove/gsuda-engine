---
rule_id: rule_20260426_highvol_lottery
status: quarantined
cluster_id: highvol_lottery
description: Suppress Buy recommendations when 20-day volatility is at least
  2.0.
trigger_conditions:
- feature: signal
  op: '='
  value: Buy
- feature: volatility_20
  op: '>='
  value: 2.0
action:
  type: suppress_trade
  reason: High volatility Buy recommendations in this failure cluster showed
    repeated loss patterns and require empirical validation before deployment.
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
cluster_evidence:
  failure_count: 36
  avg_failed_return_pct: -6.5823
  worst_return_pct: -11.9101
  rationale: A tempting high-volatility suppression that should be quarantined
    for winner damage.
sample_rows:
- trade_id: trade_highvol_000
  return_pct: -11.2455
  sector: Electrical Equipment
  month_pillar: GengChen
  jieqi_zone: first_3
  volatility_20: 2.9124
- trade_id: trade_highvol_001
  return_pct: -9.2562
  sector: Software
  month_pillar: RenShen
  jieqi_zone: middle
  volatility_20: 3.2445
- trade_id: trade_highvol_002
  return_pct: -8.6611
  sector: Secondary Batteries
  month_pillar: JiaXu
  jieqi_zone: last_3
  volatility_20: 2.2378
- trade_id: trade_highvol_005
  return_pct: -10.6871
  sector: Software
  month_pillar: JiaXu
  jieqi_zone: last_3
  volatility_20: 3.397
- trade_id: trade_highvol_006
  return_pct: -1.7532
  sector: Secondary Batteries
  month_pillar: GengChen
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
notes:
- This rule is a candidate only.
- Saju and Yi-related fields are domain-informed categorical features and
  require empirical validation.
- The validator must replace placeholder backtest statistics before any
  deployment decision.
failure_reason: winner_damage_gt_35pct
---

## Why this rule exists

This candidate was spawned from the `highvol_lottery` failed-trade cluster. The cluster contains Buy recommendations with `volatility_20 >= 2.0` that produced repeated negative outcomes, with an average failed return of -6.5823 percent and a worst observed return of -11.9101 percent.

The cluster rationale explicitly warns that this suppression may cause winner damage. For that reason, the rule should remain a candidate until the validation gate measures historical matches, cluster precision, winner damage, and 2024-2025 out-of-sample behavior.

## What it does

When a trade recommendation has `signal = Buy` and `volatility_20 >= 2.0`, this rule proposes suppressing the trade.

This is not a claim that Saju or Yi-derived features predict stock prices. Any Saju-related fields in the evidence, such as `month_pillar` or `jieqi_zone`, are treated only as domain-informed categorical features that require empirical validation before use in an active trading rule.

## Validation Result

Quarantined by the validation gate. Failure reason: winner_damage_gt_35pct.
