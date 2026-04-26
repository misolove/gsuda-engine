---
rule_id: rule_20260426_highvol_lottery
version: 0.1
status: candidate
created_at: 2026-04-26T10:22:49.940446+00:00
spawned_from_failures:
  - trade_highvol_000
  - trade_highvol_001
  - trade_highvol_002
  - trade_highvol_005
  - trade_highvol_006
trigger_conditions:
  - feature: signal
    op: "="
    value: "Buy"
  - feature: volatility_20
    op: ">="
    value: 2.0
suppression_logic: suppress_buy_signal
domain_context:
  note: Saju and Yeokhak fields are domain-informed categorical features for empirical validation, not claims that Saju predicts stock prices.
  validation_key_policy: Compact English keys are validated; original Hanja is preserved for provenance.
  observed_month_pillars:
  - validation_key: MetalDragon
    original_hanja: 庚辰
    english_label: Metal Dragon
  - validation_key: WaterMonkey
    original_hanja: 壬申
    english_label: Water Monkey
  - validation_key: WoodDog
    original_hanja: 甲戌
    english_label: Wood Dog
backtest_stats:
  historical_matches: 0
  cluster_precision: 0.0
  winner_damage_pct: 0.0
  oos_2024_2025_holds: false
---

# Rule: suppress high-volatility lottery buys

## Why this rule exists
A tempting high-volatility suppression that should be quarantined for winner damage.

The latest failure cluster contains 36 failed trades.
Average failed T+5 return: -6.5823%.

## What it does
When the Strategy Orchestrator emits a buy recommendation matching the trigger
conditions, Risk Guardian suppresses it and records this rule id as provenance.
