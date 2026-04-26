---
rule_id: rule_20260426_shinmi_semis_midvol_not_last3
status: active
action: suppress_trade
scope:
  market: KR
  asset_class: equities
  frequency: daily
trigger_conditions:
- feature: signal
  op: '='
  value: Buy
- feature: month_pillar
  op: '='
  value: 辛未
- feature: sector
  op: '='
  value: 반도체와반도체장비
- feature: volatility_20
  op: between
  value:
  - 0.6
  - 1.2
- feature: jieqi_zone
  op: not_in
  value:
  - last_3
spawned_from_cluster:
  cluster_id: shinmi_semis_midvol_not_last3
  failure_count: 71
  avg_failed_return_pct: -5.5321
  worst_return_pct: -9.7842
spawned_from_failures:
- trade_shinmi_semis_000
- trade_shinmi_semis_001
- trade_shinmi_semis_002
- trade_shinmi_semis_003
- trade_shinmi_semis_004
- trade_shinmi_semis_005
- trade_shinmi_semis_006
- trade_shinmi_semis_007
- trade_shinmi_semis_008
- trade_shinmi_semis_009
- trade_shinmi_semis_010
- trade_shinmi_semis_011
- trade_shinmi_semis_012
- trade_shinmi_semis_013
- trade_shinmi_semis_014
- trade_shinmi_semis_015
- trade_shinmi_semis_016
- trade_shinmi_semis_017
- trade_shinmi_semis_018
- trade_shinmi_semis_019
sample_evidence:
- trade_id: trade_shinmi_semis_000
  return_pct: -8.3981
  sector: 반도체와반도체장비
  month_pillar: 辛未
  jieqi_zone: first_3
  volatility_20: 0.8006
- trade_id: trade_shinmi_semis_001
  return_pct: -0.888
  sector: 반도체와반도체장비
  month_pillar: 辛未
  jieqi_zone: middle
  volatility_20: 1.1717
- trade_id: trade_shinmi_semis_002
  return_pct: -8.9404
  sector: 반도체와반도체장비
  month_pillar: 辛未
  jieqi_zone: last_4_5
  volatility_20: 1.1253
- trade_id: trade_shinmi_semis_003
  return_pct: -6.3079
  sector: 반도체와반도체장비
  month_pillar: 辛未
  jieqi_zone: first_3
  volatility_20: 0.7115
- trade_id: trade_shinmi_semis_004
  return_pct: -8.2204
  sector: 반도체와반도체장비
  month_pillar: 辛未
  jieqi_zone: middle
  volatility_20: 0.6359
backtest_stats:
  historical_matches: 75
  cluster_precision: 0.9467
  winner_damage_pct: 5.33
  avg_return_pct: -5.0165
  median_return_pct: -5.5141
  oos_matches: 30
  oos_precision: 0.8667
  oos_avg_return_pct: -4.3569
  oos_median_return_pct: -5.2104
  oos_2024_2025_holds: true
provenance:
  drafted_from: clustered_failed_trades
  drafted_at: '2026-04-26'
  validation_required: true
---

## Why this rule exists

This candidate rule was drafted from a failure cluster where Buy recommendations for Korean semiconductor and semiconductor-equipment equities showed repeated negative outcomes under a shared feature pattern.

The cluster is defined by month pillar `辛未`, sector `반도체와반도체장비`, 20-day volatility between `0.6` and `1.2`, and solar-term zone not in `last_3`. The observed failed trades had an average failed return of `-5.5321%`, with the worst sampled cluster return at `-9.7842%`.

Saju and solar-term values here are treated only as domain-informed categorical features. This rule does not assume that Saju predicts stock prices; it must pass empirical validation before deployment.

## What it does

When a proposed trade matches all trigger conditions, this rule suppresses the Buy recommendation before execution.

The validator must replace the placeholder `backtest_stats` values and decide whether this candidate is safe to promote to active rules or should remain quarantined.