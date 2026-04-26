"""Stage 1: trade logging."""

from __future__ import annotations

import json
from datetime import datetime, timezone


def log_trade(connection: object, recommendation: object) -> str:
    """Persist a trade recommendation and return its trade id."""

    trade_id = getattr(recommendation, "trade_id", "trade_stub_001")
    features = dict(getattr(recommendation, "features", {}) or {})
    ts = features.get("ts") or datetime.now(timezone.utc)

    connection.execute(
        """
        INSERT OR REPLACE INTO trade_log (
            trade_id, ts, symbol, sector, entry_price, stop_price, target_price,
            signal, rsi14, macd, macd_signal, bb_position, volatility_20,
            volume_ratio, golden_cross, d1, d2, year_pillar, month_pillar,
            day_pillar, jieqi_zone, month_progress, month_hidden_wood_weight,
            month_hidden_fire_weight, month_hidden_earth_weight,
            month_hidden_metal_weight, month_hidden_water_weight, sim_return_t5,
            applied_rules, suppressed_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            str(trade_id),
            ts,
            getattr(recommendation, "symbol", ""),
            getattr(recommendation, "sector", ""),
            float(getattr(recommendation, "entry_price", 0.0)),
            float(getattr(recommendation, "stop_price", 0.0)),
            float(getattr(recommendation, "target_price", 0.0)),
            features.get("signal", "Buy"),
            features.get("rsi14"),
            features.get("macd"),
            features.get("macd_signal"),
            features.get("bb_position"),
            features.get("volatility_20"),
            features.get("volume_ratio"),
            features.get("golden_cross"),
            features.get("d1"),
            features.get("d2"),
            features.get("year_pillar"),
            features.get("month_pillar"),
            features.get("day_pillar"),
            features.get("jieqi_zone"),
            features.get("month_progress"),
            features.get("month_hidden_wood_weight"),
            features.get("month_hidden_fire_weight"),
            features.get("month_hidden_earth_weight"),
            features.get("month_hidden_metal_weight"),
            features.get("month_hidden_water_weight"),
            features.get("sim_return_t5"),
            json.dumps(features.get("applied_rules", []), ensure_ascii=False),
            features.get("suppressed_by"),
        ],
    )
    return str(trade_id)
