---
rule_id: rule_20260426_highvol_lottery
status: quarantined
cluster_id: highvol_lottery
trigger_conditions:
- feature: signal
  op: '='
  value: Buy
- feature: volatility_20
  op: '>='
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
  rationale: A tempting high-volatility suppression that should be quarantined
    for winner damage.
domain_context:
  note: Saju and Yi-derived values are domain-informed categorical features for
    empirical validation, not claims that Saju predicts stock prices.
  provenance_policy: Romanized machine keys are validated; original Hanja is
    preserved for Saju provenance.
  observed_month_pillars:
  - romanized: GengChen
    hanja: 庚辰
    english: Metal Dragon
  - romanized: RenShen
    hanja: 壬申
    english: Water Monkey
  - romanized: JiaXu
    hanja: 甲戌
    english: Wood Dog
  observed_jieqi_zones:
  - first_3
  - middle
  - last_3
sample_provenance:
- trade_id: trade_highvol_000
  return_pct: -11.2455
  sector: Electrical Equipment
  month_pillar:
    romanized: GengChen
    hanja: 庚辰
    english: Metal Dragon
  jieqi_zone: first_3
  volatility_20: 2.9124
- trade_id: trade_highvol_001
  return_pct: -9.2562
  sector: Software
  month_pillar:
    romanized: RenShen
    hanja: 壬申
    english: Water Monkey
  jieqi_zone: middle
  volatility_20: 3.2445
- trade_id: trade_highvol_002
  return_pct: -8.6611
  sector: Secondary Batteries
  month_pillar:
    romanized: JiaXu
    hanja: 甲戌
    english: Wood Dog
  jieqi_zone: last_3
  volatility_20: 2.2378
- trade_id: trade_highvol_005
  return_pct: -10.6871
  sector: Software
  month_pillar:
    romanized: JiaXu
    hanja: 甲戌
    english: Wood Dog
  jieqi_zone: last_3
  volatility_20: 3.397
- trade_id: trade_highvol_006
  return_pct: -1.7532
  sector: Secondary Batteries
  month_pillar:
    romanized: GengChen
    hanja: 庚辰
    english: Metal Dragon
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
failure_reason: winner_damage_gt_35pct
---

## Why this rule exists

This candidate rule was spawned from the `highvol_lottery` failure cluster, where 36 failed Buy trades averaged -6.5823 percent and the worst observed return was -11.9101 percent. The cluster suggests that Buy trades with `volatility_20 >= 2.0` may include lottery-like high-volatility setups that produced repeated losses in the replay sample.

The cluster rationale also warns that this suppression may damage winners. For that reason, this rule must remain a candidate until the validator measures historical match quality, cluster precision, winner damage, and 2024-2025 out-of-sample behavior.

## What it does

When a proposed trade has `signal = Buy` and `volatility_20 >= 2.0`, this rule proposes suppressing the trade before execution.

The Saju-related fields in the provenance, including `GengChen` / `庚辰` / `Metal Dragon`, `RenShen` / `壬申` / `Water Monkey`, and `JiaXu` / `甲戌` / `Wood Dog`, are preserved as domain-informed categorical features. They are not treated as predictive claims. Their value depends on empirical validation by the backtest gate.

## Validation Result

Quarantined by the validation gate. Failure reason: winner_damage_gt_35pct.
