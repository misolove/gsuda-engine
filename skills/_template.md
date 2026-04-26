---
rule_id: rule_20260426_001
version: 0.1
status: active
created_at: 2026-04-26T13:00:00+00:00
spawned_from_failures:
  - trade_abc123
  - trade_def456
trigger_conditions:
  - feature: volatility_20
    op: ">"
    value: 35
  - feature: sector
    op: "in"
    value: ["Semiconductors", "Secondary Batteries"]
suppression_logic: suppress_buy_signal
backtest_stats:
  historical_matches: 87
  cluster_precision: 0.73
  winner_damage_pct: 2.1
  oos_2024_2025_holds: true
---

# Rule: suppress high-vol semiconductor golden cross

## Why this rule exists

Explain the failed trade pattern that spawned this rule.

## What it does

Explain the machine-checkable suppression behavior.
