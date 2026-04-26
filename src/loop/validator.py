"""Stage 4: validation gate for candidate rules."""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any

from ruamel.yaml import YAML


@dataclass(frozen=True)
class ValidationResult:
    """Backtest-gate result for a candidate rule."""

    passed: bool
    stats: dict[str, object]
    failure_reason: str | None = None


ALLOWED_FEATURES = {
    "signal",
    "sector",
    "rsi14",
    "macd",
    "macd_signal",
    "bb_position",
    "volatility_20",
    "volume_ratio",
    "golden_cross",
    "d1",
    "d2",
    "year_pillar",
    "month_pillar",
    "day_pillar",
    "year_pillar_hanja",
    "month_pillar_hanja",
    "day_pillar_hanja",
    "year_pillar_english",
    "month_pillar_english",
    "day_pillar_english",
    "jieqi_zone",
    "month_progress",
    "month_hidden_wood_weight",
    "month_hidden_fire_weight",
    "month_hidden_earth_weight",
    "month_hidden_metal_weight",
    "month_hidden_water_weight",
}


def split_frontmatter(rule_text: str) -> tuple[dict[str, Any], str]:
    """Parse a skill file into YAML metadata and markdown body."""

    if not rule_text.startswith("---\n"):
        raise ValueError("skill file must start with YAML frontmatter")
    _, rest = rule_text.split("---\n", 1)
    yaml_text, body = rest.split("\n---", 1)
    yaml = YAML(typ="safe")
    metadata = yaml.load(yaml_text) or {}
    return metadata, body.lstrip("\n")


def get_rule_id(rule_text: str) -> str:
    """Return the rule id from a skill file."""

    metadata, _ = split_frontmatter(rule_text)
    return str(metadata.get("rule_id", "rule_unknown"))


def _condition_to_sql(condition: dict[str, Any], params: list[Any]) -> str:
    feature = str(condition.get("feature", ""))
    if feature not in ALLOWED_FEATURES:
        raise ValueError(f"unsupported trigger feature: {feature}")

    op = str(condition.get("op", "=")).lower()
    value = condition.get("value")

    if op in {"=", "=="}:
        params.append(value)
        return f"{feature} = ?"
    if op in {"!=", "<>"}:
        params.append(value)
        return f"{feature} <> ?"
    if op in {">", ">=", "<", "<="}:
        params.append(value)
        return f"{feature} {op} ?"
    if op == "between":
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError("between trigger requires [min, max]")
        params.extend(value)
        return f"{feature} >= ? AND {feature} < ?"
    if op == "in":
        if not isinstance(value, list) or not value:
            raise ValueError("in trigger requires a non-empty list")
        params.extend(value)
        placeholders = ", ".join("?" for _ in value)
        return f"{feature} IN ({placeholders})"
    if op == "not_in":
        if not isinstance(value, list) or not value:
            raise ValueError("not_in trigger requires a non-empty list")
        params.extend(value)
        placeholders = ", ".join("?" for _ in value)
        return f"{feature} NOT IN ({placeholders})"

    raise ValueError(f"unsupported trigger op: {op}")


def _where_clause(trigger_conditions: list[dict[str, Any]]) -> tuple[str, list[Any]]:
    params: list[Any] = []
    sql_parts = [_condition_to_sql(condition, params) for condition in trigger_conditions]
    return " AND ".join(f"({part})" for part in sql_parts), params


def validate_rule(connection: object, rule_text: str) -> ValidationResult:
    """Run the four validation checks for a candidate rule."""

    metadata, _ = split_frontmatter(rule_text)
    trigger_conditions = metadata.get("trigger_conditions") or []
    if not isinstance(trigger_conditions, list) or not trigger_conditions:
        return ValidationResult(
            passed=False,
            stats={
                "historical_matches": 0,
                "cluster_precision": 0.0,
                "winner_damage_pct": 100.0,
                "oos_2024_2025_holds": False,
            },
            failure_reason="missing_trigger_conditions",
        )

    where_sql, params = _where_clause(trigger_conditions)
    row = connection.execute(
        f"""
        SELECT
            COUNT(*) AS historical_matches,
            SUM(CASE WHEN sim_return_t5 < 0 THEN 1 ELSE 0 END) AS failures,
            SUM(CASE WHEN sim_return_t5 >= 0 THEN 1 ELSE 0 END) AS winners,
            AVG(sim_return_t5) AS avg_return_pct,
            MEDIAN(sim_return_t5) AS median_return_pct
        FROM trade_log
        WHERE {where_sql}
        """,
        params,
    ).fetchone()

    historical_matches = int(row[0] or 0)
    failures = int(row[1] or 0)
    winners = int(row[2] or 0)
    avg_return_pct = float(row[3] or 0.0)
    median_return_pct = float(row[4] or 0.0)
    cluster_precision = failures / historical_matches if historical_matches else 0.0
    winner_damage_pct = (winners / historical_matches * 100.0) if historical_matches else 100.0

    oos_row = connection.execute(
        f"""
        SELECT
            COUNT(*) AS oos_matches,
            SUM(CASE WHEN sim_return_t5 < 0 THEN 1 ELSE 0 END) AS oos_failures,
            AVG(sim_return_t5) AS oos_avg_return_pct,
            MEDIAN(sim_return_t5) AS oos_median_return_pct
        FROM trade_log
        WHERE {where_sql}
          AND EXTRACT(YEAR FROM ts) BETWEEN 2024 AND 2025
        """,
        params,
    ).fetchone()
    oos_matches = int(oos_row[0] or 0)
    oos_failures = int(oos_row[1] or 0)
    oos_avg_return_pct = float(oos_row[2] or 0.0)
    oos_median_return_pct = float(oos_row[3] or 0.0)
    oos_precision = oos_failures / oos_matches if oos_matches else 0.0
    oos_holds = oos_matches >= 10 and oos_precision >= 0.60 and oos_median_return_pct < 0

    stats = {
        "historical_matches": historical_matches,
        "cluster_precision": round(cluster_precision, 4),
        "winner_damage_pct": round(winner_damage_pct, 2),
        "avg_return_pct": round(avg_return_pct, 4),
        "median_return_pct": round(median_return_pct, 4),
        "oos_matches": oos_matches,
        "oos_precision": round(oos_precision, 4),
        "oos_avg_return_pct": round(oos_avg_return_pct, 4),
        "oos_median_return_pct": round(oos_median_return_pct, 4),
        "oos_2024_2025_holds": oos_holds,
    }

    failures_reasons: list[str] = []
    if historical_matches < 50:
        failures_reasons.append("historical_matches_lt_50")
    if cluster_precision < 0.60:
        failures_reasons.append("cluster_precision_lt_0.60")
    if winner_damage_pct > 35.0:
        failures_reasons.append("winner_damage_gt_35pct")
    if not oos_holds:
        failures_reasons.append("oos_2024_2025_failed")

    passed = not failures_reasons
    return ValidationResult(
        passed=passed,
        stats=stats,
        failure_reason=None if passed else ", ".join(failures_reasons),
    )


def render_validated_rule(rule_text: str, result: ValidationResult) -> str:
    """Update status and backtest stats in a skill file."""

    metadata, body = split_frontmatter(rule_text)
    if hasattr(metadata.get("created_at"), "isoformat"):
        metadata["created_at"] = metadata["created_at"].isoformat()
    metadata["status"] = "active" if result.passed else "quarantined"
    metadata["backtest_stats"] = result.stats
    if result.failure_reason:
        metadata["failure_reason"] = result.failure_reason
    body = _render_validation_language(body, result)

    yaml = YAML()
    yaml.allow_unicode = True
    yaml.default_flow_style = False
    out = io.StringIO()
    yaml.dump(metadata, out)
    return f"---\n{out.getvalue()}---\n\n{body}"


def _render_validation_language(body: str, result: ValidationResult) -> str:
    """Make the markdown body agree with the final validator decision."""

    body = body.replace("\u2019", "'")
    candidate_sentence = (
        "This file is only a candidate. It must pass the validator's historical-match, "
        "cluster-precision, winner-damage, and 2024-2025 out-of-sample checks before it can be promoted."
    )
    if result.passed:
        body = body.replace("This candidate was", "This active rule was")
        body = body.replace("this candidate was", "this active rule was")
        body = body.replace("this candidate rule", "this active rule")
        body = body.replace("This candidate rule", "This active rule")
        body = body.replace(
            "The validator must replace the placeholder `backtest_stats` and decide whether the rule moves to `skills/active/` or `skills/quarantined/`.",
            "The validator replaced the placeholder `backtest_stats` and promoted the rule to `skills/active/`.",
        )
        body = body.replace(
            "It must pass empirical validation before it can be deployed.",
            "It passed empirical validation before deployment.",
        )
        body = body.replace(
            "This rule must pass the validation gate before it can be considered for active deployment.",
            "This rule passed the validation gate before active deployment.",
        )
        body = body.replace(
            "The validator must replace the placeholder backtest_stats and decide whether this candidate moves to active or quarantined.",
            "The validator replaced the placeholder backtest_stats and promoted this rule to active.",
        )
        body = body.replace(
            "The placeholder backtest statistics are intentionally set to zero or false. The validator is responsible for replacing them after historical-match, cluster-precision, winner-damage, and 2024-2025 out-of-sample checks.",
            "The validator replaced the placeholder backtest statistics after historical-match, cluster-precision, winner-damage, and 2024-2025 out-of-sample checks.",
        )
        body = body.replace(
            "The rule remains a candidate until the validator replaces the placeholder backtest statistics and confirms that the suppression passes the historical-match, cluster-precision, winner-damage, and 2024-2025 out-of-sample gates.",
            "The validator replaced the placeholder backtest statistics and confirmed that the suppression passes the historical-match, cluster-precision, winner-damage, and 2024-2025 out-of-sample gates.",
        )
        replacement = (
            "This rule passed the validation gate and was promoted to active status. "
            "Risk Guardian can load it on the next recommendation."
        )
    else:
        replacement = (
            "This rule did not pass the validation gate and remains quarantined. "
            f"Failure reason: {result.failure_reason}."
        )
    if candidate_sentence in body:
        return body.replace(candidate_sentence, replacement)

    validation_section = (
        "\n\n## Validation Result\n\n"
        + (
            "Passed the validation gate and was promoted to active status."
            if result.passed
            else f"Quarantined by the validation gate. Failure reason: {result.failure_reason}."
        )
    )
    return body.rstrip() + validation_section + "\n"
