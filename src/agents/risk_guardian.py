"""Risk Guardian stub for loading and applying validated rules."""

from __future__ import annotations

from pathlib import Path


def load_active_rules(skills_dir: Path = Path("skills/active")) -> list[Path]:
    """Return active rule files that should be evaluated for each trade."""

    if not skills_dir.exists():
        return []
    return sorted(skills_dir.glob("*.md"))


def apply_rules(recommendation: object, rules: list[Path]) -> tuple[bool, str | None]:
    """Return whether a recommendation is allowed and the suppressing rule id."""

    _ = recommendation
    _ = rules
    return True, None
