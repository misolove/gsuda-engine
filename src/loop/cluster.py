"""Stage 3a: cluster similar failure cases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FailureCluster:
    """A group of failure cases with a shared feature pattern."""

    cluster_id: str
    trade_ids: list[str]
    summary: dict[str, object]


def cluster_failures(connection: object, min_size: int = 15) -> list[FailureCluster]:
    """Return failure clusters large enough to draft candidate rules."""

    clusters: list[FailureCluster] = []

    specs = [
        (
            "xinwei_semis_midvol_not_last3",
            """
            signal = 'Buy'
            AND month_pillar = 'XinWei'
            AND sector = 'Semiconductors and Semiconductor Equipment'
            AND volatility_20 >= 0.6
            AND volatility_20 < 1.2
            AND jieqi_zone <> 'last_3'
            """,
            [
                {"feature": "signal", "op": "=", "value": "Buy"},
                {"feature": "month_pillar", "op": "=", "value": "XinWei"},
                {
                    "feature": "sector",
                    "op": "=",
                    "value": "Semiconductors and Semiconductor Equipment",
                },
                {"feature": "volatility_20", "op": "between", "value": [0.6, 1.2]},
                {"feature": "jieqi_zone", "op": "not_in", "value": ["last_3"]},
            ],
            "Suppress XinWei semiconductor buys outside the final three solar-term days.",
        ),
        (
            "highvol_lottery",
            """
            signal = 'Buy'
            AND volatility_20 >= 2.0
            """,
            [
                {"feature": "signal", "op": "=", "value": "Buy"},
                {"feature": "volatility_20", "op": ">=", "value": 2.0},
            ],
            "A tempting high-volatility suppression that should be quarantined for winner damage.",
        ),
    ]

    for cluster_id, where_sql, trigger_conditions, rationale in specs:
        rows = connection.execute(
            f"""
            SELECT
                t.trade_id,
                t.sim_return_t5,
                t.sector,
                t.month_pillar,
                t.jieqi_zone,
                t.volatility_20
            FROM failure_cases f
            JOIN trade_log t USING (trade_id)
            WHERE {where_sql}
            ORDER BY t.trade_id
            """
        ).fetchall()
        if len(rows) < min_size:
            continue
        returns = [float(row[1]) for row in rows]
        clusters.append(
            FailureCluster(
                cluster_id=cluster_id,
                trade_ids=[str(row[0]) for row in rows],
                summary={
                    "cluster_id": cluster_id,
                    "failure_count": len(rows),
                    "avg_failed_return_pct": round(sum(returns) / len(returns), 4),
                    "worst_return_pct": round(min(returns), 4),
                    "trigger_conditions": trigger_conditions,
                    "rationale": rationale,
                    "sample_rows": [
                        {
                            "trade_id": row[0],
                            "return_pct": row[1],
                            "sector": row[2],
                            "month_pillar": row[3],
                            "jieqi_zone": row[4],
                            "volatility_20": row[5],
                        }
                        for row in rows[:5]
                    ],
                },
            )
        )

    return clusters
