"""Strategy Orchestrator stub.

The real MVP implementation will emit simulated trade recommendations with
the full feature vector required by the feedback loop.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TradeRecommendation:
    """A buy recommendation plus the feature vector needed for provenance."""

    trade_id: str
    symbol: str
    sector: str
    entry_price: float
    stop_price: float
    target_price: float
    features: dict[str, object]


def emit_recommendation() -> TradeRecommendation:
    """Return one simulated recommendation.

    Block 2/3 will replace this placeholder with deterministic simulated
    historical replay data.
    """

    return TradeRecommendation(
        trade_id="trade_stub_001",
        symbol="005930",
        sector="반도체",
        entry_price=70000.0,
        stop_price=67200.0,
        target_price=74200.0,
        features={
            "rsi14": 62.0,
            "macd": 1.2,
            "macd_signal": 0.9,
            "bb_position": 0.78,
            "volatility_20": 35.5,
            "volume_ratio": 1.8,
            "golden_cross": 1.0,
            "d1": "경",
            "d2": "인",
            "signal": "Buy",
            "year_pillar": "丙午",
            "month_pillar": "辛未",
            "day_pillar": "庚寅",
            "jieqi_zone": "middle",
            "month_progress": 0.52,
            "month_hidden_wood_weight": 0.2,
            "month_hidden_fire_weight": 0.3,
            "month_hidden_earth_weight": 0.5,
            "month_hidden_metal_weight": 0.0,
            "month_hidden_water_weight": 0.0,
            "sim_return_t5": -3.2,
        },
    )
