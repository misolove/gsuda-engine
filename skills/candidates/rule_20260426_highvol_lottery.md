---
rule_id: rule_20260426_highvol_lottery
status: candidate
cluster_id: highvol_lottery
description: Suppress Buy recommendations when 20 day volatility is at or above 2.0.
trigger_conditions:
  - feature: signal
    op: "="
    value: Buy
  - feature: volatility_20
    op: ">="
    value: 2.0
action:
  type: suppress_trade
  reason: highvol_lottery_failure_cluster
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
failure_summary:
  failure_count: 36
  avg_failed_return_pct: -6.5823
  worst_return_pct: -11.9101
domain_context:
  note: Saju and Yi derived values are domain-informed categorical features for empirical validation, not claims that Saju predicts stock prices.
  validation_keys_are_compact_english: true
  pillar_notation: Compact English keys are validated. Original Hanja is preserved for Saju provenance.
  observed_month_pillars:
    - validation_key: MetalDragon
      original_hanja: 庚辰
      english_display_label: Metal Dragon
    - validation_key: WaterMonkey
      original_hanja: 壬申
      english_display_label: Water Monkey
    - validation_key: WoodDog
      original_hanja: 甲戌
      english_display_label: Wood Dog
  observed_jieqi_zones:
    - first_3
    - middle
    - last_3
backtest_stats:
  historical_matches: 0
  cluster_precision: 0.0
  winner_damage_pct: 0.0
  oos_2024_2025_passed: false
  passed_validation_gate: false
---

## Why this rule exists

This candidate was spawned from the highvol_lottery failure cluster, where Buy recommendations with volatility_20 at or above 2.0 showed repeated failed outcomes. The cluster contains 36 failures with an average failed return of -6.5823 percent and a worst observed return of -11.9101 percent.

The cluster rationale warns that this is a tempting high-volatility suppression rule, but it may damage winners. It must remain a candidate until the validator replaces the placeholder backtest stats and confirms that the rule passes the validation gate.

## What it does

When a trade has signal equal to Buy and volatility_20 greater than or equal to 2.0, this rule suppresses the trade recommendation.

The rule preserves provenance from the failed trades and retains domain-informed categorical context, including compact English validation keys and original Hanja month-pillar notation. These features are included for empirical validation only and do not imply that Saju predicts stock prices.