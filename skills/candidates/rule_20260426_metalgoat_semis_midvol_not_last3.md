---
rule_id: rule_20260426_metalgoat_semis_midvol_not_last3
version: 0.1
status: candidate
created_at: 2026-04-26T00:00:00+00:00
spawned_from_failures:
  - trade_metalgoat_semis_000
  - trade_metalgoat_semis_001
  - trade_metalgoat_semis_002
  - trade_metalgoat_semis_003
  - trade_metalgoat_semis_004
trigger_conditions:
  - feature: signal
    op: "="
    value: "Buy"
  - feature: month_pillar
    op: "="
    value: "MetalGoat"
  - feature: sector
    op: "="
    value: "Semiconductors and Semiconductor Equipment"
  - feature: volatility_20
    op: "between"
    value: [0.6, 1.2]
  - feature: jieqi_zone
    op: "not_in"
    value: ["last_3"]
suppression_logic: suppress_buy_signal
domain_context:
  note: Saju and Yeokhak fields are domain-informed categorical features for empirical validation, not claims that Saju predicts stock prices.
  validation_key_policy: Compact English keys are validated; original Hanja is preserved for provenance.
  observed_month_pillars:
  - validation_key: MetalGoat
    original_hanja: 辛未
    english_label: Metal Goat
backtest_stats:
  historical_matches: 0
  cluster_precision: 0.0
  winner_damage_pct: 0.0
  oos_2024_2025_holds: false
---

# Rule: suppress Metal Goat semiconductor mid-vol buys

## Why this rule exists
Suppress Metal Goat semiconductor buys outside the final three solar-term days.

The latest failure cluster contains 71 failed trades.
Average failed T+5 return: -5.5321%.

## What it does
When the Strategy Orchestrator emits a buy recommendation matching the trigger
conditions, Risk Guardian suppresses it and records this rule id as provenance.
