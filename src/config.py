"""Project configuration for the gsuda-engine hackathon MVP."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - allows lightweight import before install
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    """Runtime settings shared by scripts and loop modules."""

    db_path: Path = PROJECT_ROOT / os.getenv("GSUDA_DB_PATH", "data/gsuda.duckdb")
    cluster_min_failures: int = 15
    draft_trigger_failures: int = 20
    simulation_seed: int = 20260426
    simulated_trade_count: int = 100
    use_mock_claude: bool = os.getenv("GSUDA_USE_MOCK_CLAUDE", "true").lower() == "true"
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")
    claude_agent_model: str = os.getenv("CLAUDE_AGENT_MODEL", "opus")
    agent_sdk_budget_usd: float = float(os.getenv("GSUDA_AGENT_SDK_BUDGET_USD", "5"))


settings = Settings()
