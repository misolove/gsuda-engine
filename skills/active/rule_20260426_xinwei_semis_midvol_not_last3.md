---
rule_id: rule_20260426_xinwei_semis_midvol_not_last3
status: active
cluster_id: xinwei_semis_midvol_not_last3
action: suppress_trade
decision: block
scope:
  market: Korean equities
  mode: simulated_historical_replay
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
cluster_evidence:
  failure_count: 71
  avg_failed_return_pct: -5.5321
  worst_return_pct: -9.7842
  sample_failed_trades:
  - trade_id: trade_xinwei_semis_000
    return_pct: -8.3981
    sector: Semiconductors and Semiconductor Equipment
    month_pillar: XinWei
    jieqi_zone: first_3
    volatility_20: 0.8006
  - trade_id: trade_xinwei_semis_001
    return_pct: -0.888
    sector: Semiconductors and Semiconductor Equipment
    month_pillar: XinWei
    jieqi_zone: middle
    volatility_20: 1.1717
  - trade_id: trade_xinwei_semis_002
    return_pct: -8.9404
    sector: Semiconductors and Semiconductor Equipment
    month_pillar: XinWei
    jieqi_zone: last_4_5
    volatility_20: 1.1253
  - trade_id: trade_xinwei_semis_003
    return_pct: -6.3079
    sector: Semiconductors and Semiconductor Equipment
    month_pillar: XinWei
    jieqi_zone: first_3
    volatility_20: 0.7115
  - trade_id: trade_xinwei_semis_004
    return_pct: -8.2204
    sector: Semiconductors and Semiconductor Equipment
    month_pillar: XinWei
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
notes:
  rationale: Suppress XinWei semiconductor buys outside the final three
    solar-term days.
  validation_required: true
  saju_disclaimer: Saju and Yi-derived fields are domain-informed categorical
    features and do not imply prediction of stock prices without empirical
    validation.
---

## Why this rule exists

This active rule was drafted from a failed-trade cluster with 71 observed failures, an average failed return of -5.5321 percent, and a worst observed return of -9.7842 percent. The shared pattern is a Buy signal in the semiconductor sector during the XinWei month pillar, with mid-range 20-day volatility and a solar-term zone outside `last_3`.

The Saju and solar-term fields are treated only as categorical feature-engineering inputs. This rule must pass the validation gate before it can become active.

## What it does

When all trigger conditions match, this rule suppresses the trade recommendation. It blocks only Buy signals where:

- `month_pillar` is `XinWei`
- `sector` is `Semiconductors and Semiconductor Equipment`
- `volatility_20` is between `0.6` and `1.2`
- `jieqi_zone` is not `last_3`

The placeholder backtest fields are intentionally unset and must be replaced by the validator.

## Validation Result

Passed the validation gate and was promoted to active status.
