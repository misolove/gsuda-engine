"""Stage 2: outcome tracking for simulated trades."""

from __future__ import annotations

from datetime import datetime, timezone


def tag_trade_outcomes(connection: object, holding_days: int = 5) -> dict[str, int]:
    """Compute simulated outcomes and write loss cases.

    The hackathon demo stores deterministic T+5 returns in `trade_log` so the
    closed loop can run from a clean clone without live broker integration.
    """

    tagged_at = datetime.now(timezone.utc)
    connection.execute(
        """
        INSERT OR REPLACE INTO failure_cases (
            trade_id, outcome, return_pct, holding_days, tagged_at
        )
        SELECT
            trade_id,
            CASE WHEN sim_return_t5 <= -4.0 THEN 'stopped_out' ELSE 'loss' END,
            sim_return_t5,
            ?,
            ?
        FROM trade_log
        WHERE sim_return_t5 < 0
        """,
        [holding_days, tagged_at],
    )

    row = connection.execute(
        """
        SELECT
            SUM(CASE WHEN sim_return_t5 >= 0 THEN 1 ELSE 0 END) AS win,
            SUM(CASE WHEN sim_return_t5 < 0 AND sim_return_t5 > -4.0 THEN 1 ELSE 0 END) AS loss,
            SUM(CASE WHEN sim_return_t5 <= -4.0 THEN 1 ELSE 0 END) AS stopped_out
        FROM trade_log
        """
    ).fetchone()
    return {
        "win": int(row[0] or 0),
        "loss": int(row[1] or 0),
        "stopped_out": int(row[2] or 0),
    }
