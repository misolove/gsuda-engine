"""Run the full gsuda-engine feedback loop demo."""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from _bootstrap import add_project_root_to_path

PROJECT_ROOT = add_project_root_to_path()

from src.agents.orchestrator import TradeRecommendation
from src.agents.risk_guardian import load_active_rules
from src.config import settings
from src.db.conn import connect
from src.loop.cluster import cluster_failures
from src.loop.outcome_tracker import tag_trade_outcomes
from src.loop.rule_drafter import draft_rule
from src.loop.trade_logger import log_trade
from src.loop.validator import get_rule_id, render_validated_rule, validate_rule

PILLARS = {
    "FireHorse": {"hanja": "丙午", "english": "Fire Horse"},
    "WoodSnake": {"hanja": "乙巳", "english": "Wood Snake"},
    "WoodRat": {"hanja": "甲子", "english": "Wood Rat"},
    "WoodOx": {"hanja": "乙丑", "english": "Wood Ox"},
    "FireTiger": {"hanja": "丙寅", "english": "Fire Tiger"},
    "FireRabbit": {"hanja": "丁卯", "english": "Fire Rabbit"},
    "EarthDragon": {"hanja": "戊辰", "english": "Earth Dragon"},
    "EarthSnake": {"hanja": "己巳", "english": "Earth Snake"},
    "MetalHorse": {"hanja": "庚午", "english": "Metal Horse"},
    "MetalGoat": {"hanja": "辛未", "english": "Metal Goat"},
    "WaterMonkey": {"hanja": "壬申", "english": "Water Monkey"},
    "WaterRooster": {"hanja": "癸酉", "english": "Water Rooster"},
    "MetalDragon": {"hanja": "庚辰", "english": "Metal Dragon"},
    "MetalTiger": {"hanja": "庚寅", "english": "Metal Tiger"},
    "WoodDog": {"hanja": "甲戌", "english": "Wood Dog"},
    "EarthRabbit": {"hanja": "己卯", "english": "Earth Rabbit"},
    "WaterDragon": {"hanja": "壬辰", "english": "Water Dragon"},
    "FireRooster": {"hanja": "丁酉", "english": "Fire Rooster"},
}


def banner(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def _init_schema(con: object) -> None:
    con.execute((PROJECT_ROOT / "src/db/schema.sql").read_text(encoding="utf-8"))


def _reset_demo_state(con: object) -> None:
    con.execute("DELETE FROM failure_cases")
    con.execute("DELETE FROM rule_deployments")
    con.execute("DELETE FROM trade_log")
    for directory in ["skills/active", "skills/quarantined", "skills/candidates"]:
        path = PROJECT_ROOT / directory
        path.mkdir(parents=True, exist_ok=True)
        for generated in path.glob("rule_20260426_*.md"):
            generated.unlink()
        for generated in path.glob("rule_20260426_*_cluster.json"):
            generated.unlink()


def _pillar_parts(pillar: str) -> tuple[str, str]:
    element, animal = PILLARS[pillar]["english"].split(" ", 1)
    return element, animal


def _features(
    *,
    ts: datetime,
    signal: str,
    year_pillar: str,
    month_pillar: str,
    day_pillar: str,
    jieqi_zone: str,
    volatility_20: float,
    sim_return_t5: float,
    rng: random.Random,
) -> dict[str, object]:
    d1, d2 = _pillar_parts(day_pillar)
    hidden = {
        "MetalGoat": (0.2, 0.3, 0.5, 0.0, 0.0),
        "MetalDragon": (0.2, 0.0, 0.6, 0.0, 0.2),
    }.get(month_pillar, (0.2, 0.2, 0.3, 0.2, 0.1))
    return {
        "ts": ts,
        "signal": signal,
        "rsi14": round(rng.uniform(42, 71), 2),
        "macd": round(rng.uniform(-1.2, 2.8), 4),
        "macd_signal": round(rng.uniform(-1.0, 2.0), 4),
        "bb_position": round(rng.uniform(0.35, 1.08), 4),
        "volatility_20": volatility_20,
        "volume_ratio": round(rng.uniform(0.8, 2.8), 4),
        "golden_cross": 1.0 if rng.random() > 0.25 else 0.0,
        "d1": d1,
        "d2": d2,
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "day_pillar": day_pillar,
        "year_pillar_hanja": PILLARS[year_pillar]["hanja"],
        "month_pillar_hanja": PILLARS[month_pillar]["hanja"],
        "day_pillar_hanja": PILLARS[day_pillar]["hanja"],
        "year_pillar_english": PILLARS[year_pillar]["english"],
        "month_pillar_english": PILLARS[month_pillar]["english"],
        "day_pillar_english": PILLARS[day_pillar]["english"],
        "jieqi_zone": jieqi_zone,
        "month_progress": round(rng.uniform(0.08, 0.92), 4),
        "month_hidden_wood_weight": hidden[0],
        "month_hidden_fire_weight": hidden[1],
        "month_hidden_earth_weight": hidden[2],
        "month_hidden_metal_weight": hidden[3],
        "month_hidden_water_weight": hidden[4],
        "sim_return_t5": sim_return_t5,
    }


def _recommendations() -> list[TradeRecommendation]:
    rng = random.Random(settings.simulation_seed)
    days = ["WoodRat", "WoodOx", "FireTiger", "FireRabbit", "EarthDragon", "EarthSnake", "MetalHorse", "MetalGoat", "WaterMonkey", "WaterRooster"]
    recs: list[TradeRecommendation] = []

    def add(
        *,
        family: str,
        idx: int,
        year: int,
        symbol: str,
        sector: str,
        month_pillar: str,
        jieqi_zone: str,
        volatility_20: float,
        sim_return_t5: float,
    ) -> None:
        trade_id = f"trade_{family}_{idx:03d}"
        entry = round(rng.uniform(9000, 90000), 2)
        ts = datetime(year, ((idx % 12) + 1), ((idx % 20) + 1), 0, 0, tzinfo=timezone.utc)
        recs.append(
            TradeRecommendation(
                trade_id=trade_id,
                symbol=symbol,
                sector=sector,
                entry_price=entry,
                stop_price=round(entry * 0.96, 2),
                target_price=round(entry * 1.08, 2),
                features=_features(
                    ts=ts,
                    signal="Buy",
                    year_pillar="FireHorse" if year >= 2026 else "WoodSnake",
                    month_pillar=month_pillar,
                    day_pillar=days[idx % len(days)],
                    jieqi_zone=jieqi_zone,
                    volatility_20=volatility_20,
                    sim_return_t5=sim_return_t5,
                    rng=rng,
                ),
            )
        )

    # Active-rule demo cluster: Metal Goat semiconductor mid-volatility buys are
    # mostly losses, and the 2024-2025 holdout stays negative.
    for i in range(75):
        year = 2024 if i >= 45 else 2021 + (i % 3)
        loss = i < 51 or i >= 55
        add(
            family="metalgoat_semis",
            idx=i,
            year=year,
            symbol=f"09{i % 80:04d}",
            sector="Semiconductors and Semiconductor Equipment",
            month_pillar="MetalGoat",
            jieqi_zone=["first_3", "middle", "last_4_5"][i % 3],
            volatility_20=round(rng.uniform(0.62, 1.18), 4),
            sim_return_t5=round(rng.uniform(-9.8, -0.4), 4) if loss else round(rng.uniform(0.4, 5.5), 4),
        )

    # Contrast set: same month/sector but final solar-term days. These winners
    # are the reason the active rule excludes `last_3`.
    for i in range(18):
        add(
            family="metalgoat_last3",
            idx=i,
            year=2024 + (i % 2),
            symbol=f"08{i % 40:04d}",
            sector="Semiconductors and Semiconductor Equipment",
            month_pillar="MetalGoat",
            jieqi_zone="last_3",
            volatility_20=round(rng.uniform(0.62, 1.18), 4),
            sim_return_t5=round(rng.uniform(1.0, 9.5), 4),
        )

    # Quarantine demo cluster: high-volatility buys contain plenty of failures
    # but damage too many winners to pass the gate.
    for i in range(60):
        loss = i % 5 in {0, 1, 2}
        add(
            family="highvol",
            idx=i,
            year=2023 + (i % 3),
            symbol=f"12{i % 70:04d}",
            sector=["Electrical Equipment", "Software", "Secondary Batteries", "Biotech"][i % 4],
            month_pillar=["MetalDragon", "WaterMonkey", "WoodDog"][i % 3],
            jieqi_zone=["first_3", "middle", "last_3"][i % 3],
            volatility_20=round(rng.uniform(2.05, 3.4), 4),
            sim_return_t5=round(rng.uniform(-12.0, -0.7), 4) if loss else round(rng.uniform(2.0, 22.0), 4),
        )

    # Neutral background trades so the loop looks like a market replay instead
    # of only two handcrafted groups.
    for i in range(25):
        add(
            family="background",
            idx=i,
            year=2022 + (i % 4),
            symbol=f"03{i % 50:04d}",
            sector=["Cosmetics", "Machinery", "IT Services", "Securities"][i % 4],
            month_pillar=["EarthRabbit", "EarthDragon", "WaterDragon", "FireRooster"][i % 4],
            jieqi_zone=["first_4_5", "middle", "last_4_5"][i % 3],
            volatility_20=round(rng.uniform(0.25, 1.45), 4),
            sim_return_t5=round(rng.uniform(-4.5, 7.5), 4),
        )

    return recs


def _write_deployment(con: object, rule_id: str, status: str, stats: dict[str, object], path: Path) -> None:
    con.execute(
        """
        INSERT OR REPLACE INTO rule_deployments (
            rule_id, status, spawned_from, backtest_stats, created_at, file_path
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            rule_id,
            status,
            "[]",
            json.dumps(stats, ensure_ascii=False),
            datetime.now(timezone.utc),
            str(path.relative_to(PROJECT_ROOT)),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full gsuda-engine feedback loop demo.")
    parser.add_argument(
        "--agent-sdk",
        action="store_true",
        help="Use Claude Agent SDK to write candidate rule files instead of deterministic mock drafting.",
    )
    args = parser.parse_args()

    con = connect()
    try:
        _init_schema(con)
        _reset_demo_state(con)

        banner("Stage 1: Trade fires")
        recs = _recommendations()
        for rec in recs:
            log_trade(con, rec)
        print(f"Logged {len(recs)} simulated recommendations with full feature vectors.")
        print("Feature emphasis: year/month/day pillars, original Hanja provenance, jieqi_zone, hidden-stem weights, technicals.")

        banner("Stage 2: Outcome tracker")
        counts = tag_trade_outcomes(con, holding_days=5)
        print(
            f"Tagged outcomes: {counts['win']} wins, {counts['loss']} losses, "
            f"{counts['stopped_out']} stopped_out."
        )

        banner("Stage 3: Cluster + Claude drafts rule")
        clusters = cluster_failures(con, min_size=settings.cluster_min_failures)
        print(f"Found {len(clusters)} failure clusters above min_size={settings.cluster_min_failures}.")
        if args.agent_sdk:
            print("Drafting mode: Claude Agent SDK writes candidate skill files in skills/candidates/.")
        else:
            print("Drafting mode: deterministic mock, safe for clean-clone judge runs.")

        drafted: list[tuple[str, str]] = []
        for cluster in clusters:
            print(
                f"- {cluster.cluster_id}: {len(cluster.trade_ids)} failures, "
                f"avg failed T+5 {cluster.summary['avg_failed_return_pct']}%"
            )
            drafted.append(
                (
                    cluster.cluster_id,
                    draft_rule(cluster, use_mock=not args.agent_sdk, use_agent_sdk=args.agent_sdk),
                )
            )

        banner("Stage 4: Backtest gate")
        for cluster_id, rule_text in drafted:
            result = validate_rule(con, rule_text)
            final_text = render_validated_rule(rule_text, result)
            rule_id = get_rule_id(final_text)
            status = "active" if result.passed else "quarantined"
            out_dir = PROJECT_ROOT / "skills" / status
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{rule_id}.md"
            out_path.write_text(final_text, encoding="utf-8")
            _write_deployment(con, rule_id, status, result.stats, out_path)
            marker = "PASS" if result.passed else "QUARANTINE"
            print(f"[{marker}] {rule_id} from {cluster_id}")
            print(f"  stats={json.dumps(result.stats, ensure_ascii=False)}")
            if result.failure_reason:
                print(f"  reason={result.failure_reason}")

        banner("Stage 5: Deployment")
        active_rules = load_active_rules(PROJECT_ROOT / "skills/active")
        quarantined = sorted((PROJECT_ROOT / "skills/quarantined").glob("rule_20260426_*.md"))
        print(f"Risk Guardian loaded {len(active_rules)} active rule(s):")
        for path in active_rules:
            print(f"  - {path.relative_to(PROJECT_ROOT)}")
        print(f"Quarantined rule files: {len(quarantined)}")
        for path in quarantined:
            print(f"  - {path.relative_to(PROJECT_ROOT)}")
        print()
        print("Claude is creative; the validation gate is the judge.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
