---
rule_id: rule_20260426_xinwei_semis_midvol_not_last3
status: active
cluster_id: xinwei_semis_midvol_not_last3
rule_type: suppression
created_date: '2026-04-26'
provenance:
  spawned_from_failures:
  - trade_xinwei_semis_000
  - trade_xinwei_semis_001
  - trade_xinwei_semis_002
  - trade_xinwei_semis_003
  - trade_xinwei_semis_004
  - trade_xinwei_semis_005
  - trade_xinwei_semis_006
  - trade_xinwei_semis_007
  - trade_xinwei_semis_008
  - trade_xinwei_semis_009
  - trade_xinwei_semis_010
  - trade_xinwei_semis_011
  - trade_xinwei_semis_012
  - trade_xinwei_semis_013
  - trade_xinwei_semis_014
  - trade_xinwei_semis_015
  - trade_xinwei_semis_016
  - trade_xinwei_semis_017
  - trade_xinwei_semis_018
  - trade_xinwei_semis_019
  failure_count: 71
  avg_failed_return_pct: -5.5321
  worst_return_pct: -9.7842
trigger_conditions:
- feature: signal
  op: '='
  value: Buy
- feature: month_pillar
  op: '='
  value: XinWei
- feature: sector
  op: '='
  value: Semiconductors and Semiconductor Equipment
- feature: volatility_20
  op: between
  value:
  - 0.6
  - 1.2
- feature: jieqi_zone
  op: not_in
  value:
  - last_3
domain_context:
  feature_family: saju_categorical
  validation_note: Saju and solar-term fields are domain-informed categorical
    features and must be empirically validated before deployment. This rule does
    not claim that Saju predicts stock prices.
  month_pillar:
    romanized: XinWei
    hanja: 辛未
    english: Metal Goat
  notation_note: Romanized machine keys are used for validation while original
    Hanja is preserved for provenance.
action:
  type: suppress_trade
  applies_to_signal: Buy
  reason: Suppress XinWei semiconductor buys outside the final three solar-term
    days when 20-day volatility is mid-range.
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
---

## Why this rule exists

This active rule was drafted from a cluster of failed simulated trades in semiconductor names where Buy signals appeared during the XinWei month pillar, preserved as 辛未 and labeled Metal Goat, with mid-range 20-day volatility. The cluster showed repeated losses outside the final three solar-term days.

The Saju and solar-term fields are treated only as domain-informed categorical features. They require empirical validation before any deployment decision.

## What it does

When a trade is a Buy signal for the Semiconductors and Semiconductor Equipment sector, with `month_pillar = XinWei`, `volatility_20` between `0.6` and `1.2`, and `jieqi_zone` not in `last_3`, this rule suppresses the trade.

The validator must replace the placeholder backtest statistics and decide whether this candidate becomes active or quarantined.

## Validation Result

Passed the validation gate and was promoted to active status.
