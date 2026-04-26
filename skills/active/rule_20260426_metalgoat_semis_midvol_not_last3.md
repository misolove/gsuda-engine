---
rule_id: rule_20260426_metalgoat_semis_midvol_not_last3
status: active
rule_type: suppression
cluster_id: metalgoat_semis_midvol_not_last3
created_date: '2026-04-26'
description: Suppress Buy recommendations for semiconductor trades with
  MetalGoat month pillar, mid-range 20-day volatility, and jieqi_zone outside
  last_3.
trigger_conditions:
- feature: signal
  op: '='
  value: Buy
- feature: month_pillar
  op: '='
  value: MetalGoat
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
action:
  type: suppress_trade
  reason: Historical failure cluster showed losses for Metal Goat semiconductor
    Buy trades outside the final three solar-term days.
spawned_from_failures:
- trade_metalgoat_semis_000
- trade_metalgoat_semis_001
- trade_metalgoat_semis_002
- trade_metalgoat_semis_003
- trade_metalgoat_semis_004
- trade_metalgoat_semis_005
- trade_metalgoat_semis_006
- trade_metalgoat_semis_007
- trade_metalgoat_semis_008
- trade_metalgoat_semis_009
- trade_metalgoat_semis_010
- trade_metalgoat_semis_011
- trade_metalgoat_semis_012
- trade_metalgoat_semis_013
- trade_metalgoat_semis_014
- trade_metalgoat_semis_015
- trade_metalgoat_semis_016
- trade_metalgoat_semis_017
- trade_metalgoat_semis_018
- trade_metalgoat_semis_019
cluster_evidence:
  failure_count: 71
  avg_failed_return_pct: -5.5321
  worst_return_pct: -9.7842
domain_context:
  saju_feature_type: domain_informed_categorical_feature
  validation_note: Saju and Yi-derived fields are categorical features for
    empirical validation, not claims that Saju predicts stock prices.
  month_pillar:
    validation_key: MetalGoat
    hanja: 辛未
    english_label: Metal Goat
  notation_note: Compact English keys are used for machine validation. Original
    Hanja is preserved for provenance.
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

This active rule was drafted from a clustered set of failed simulated trades. The cluster contained Buy recommendations in the semiconductor sector where the month pillar categorical feature was MetalGoat, original Hanja 辛未, and 20-day volatility was between 0.6 and 1.2. These failures occurred when `jieqi_zone` was not `last_3`.

The rule preserves provenance from the failed trade IDs and the original Saju notation. It does not assume that Saju predicts prices. It treats the month pillar as a domain-informed categorical feature that passed empirical validation before deployment.

## What it does

If a new recommendation is a Buy for `Semiconductors and Semiconductor Equipment`, has `month_pillar = MetalGoat`, has `volatility_20` between 0.6 and 1.2, and has `jieqi_zone` outside `last_3`, this active rule suppresses the trade.

The validator replaced the placeholder backtest statistics and promoted this rule to active.

## Validation Result

Passed the validation gate and was promoted to active status.
