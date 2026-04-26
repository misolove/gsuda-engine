"""Stage 3b: draft candidate rules from failure clusters."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

from src.config import PROJECT_ROOT, settings
from src.loop.cluster import FailureCluster


def draft_rule(
    cluster: FailureCluster,
    use_mock: bool = True,
    use_agent_sdk: bool = False,
    project_root: Path = PROJECT_ROOT,
) -> str:
    """Return a YAML+markdown skill file for a candidate suppression rule."""

    if use_agent_sdk:
        return asyncio.run(_draft_rule_with_agent_sdk(cluster, project_root))

    if not use_mock:
        raise NotImplementedError("Direct Claude API drafting is intentionally deferred; use --agent-sdk.")

    return _draft_rule_with_mock(cluster)


def _yaml_value(value: object) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _format_conditions(conditions: list[dict[str, object]]) -> str:
    lines: list[str] = []
    for condition in conditions:
        lines.extend(
            [
                f"  - feature: {condition['feature']}",
                f"    op: {_yaml_value(condition['op'])}",
                f"    value: {_yaml_value(condition['value'])}",
            ]
        )
    return "\n".join(lines)


def _draft_rule_with_mock(cluster: FailureCluster) -> str:
    created_at = datetime.now(timezone.utc).isoformat()
    spawned = "\n".join(f"  - {trade_id}" for trade_id in cluster.trade_ids[:5])
    conditions = cluster.summary.get("trigger_conditions", [])
    condition_text = _format_conditions(conditions if isinstance(conditions, list) else [])
    if not condition_text:
        condition_text = '  - feature: volatility_20\n    op: ">="\n    value: 2.0'
    title = {
        "xinwei_semis_midvol_not_last3": "suppress XinWei semiconductor mid-vol buys",
        "highvol_lottery": "suppress high-volatility lottery buys",
    }.get(cluster.cluster_id, f"suppress {cluster.cluster_id}")
    rationale = str(cluster.summary.get("rationale", "Clustered losses share a repeated feature pattern."))

    return f"""---
rule_id: rule_20260426_{cluster.cluster_id}
version: 0.1
status: candidate
created_at: {created_at}
spawned_from_failures:
{spawned or "  - trade_stub_001"}
trigger_conditions:
{condition_text}
suppression_logic: suppress_buy_signal
backtest_stats:
  historical_matches: 0
  cluster_precision: 0.0
  winner_damage_pct: 0.0
  oos_2024_2025_holds: false
---

# Rule: {title}

## Why this rule exists
{rationale}

The latest failure cluster contains {len(cluster.trade_ids)} failed trades.
Average failed T+5 return: {cluster.summary.get("avg_failed_return_pct", "n/a")}%.

## What it does
When the Strategy Orchestrator emits a buy recommendation matching the trigger
conditions, Risk Guardian suppresses it and records this rule id as provenance.
"""


async def _draft_rule_with_agent_sdk(cluster: FailureCluster, project_root: Path) -> str:
    """Ask Claude Agent SDK to write the candidate skill file in the workspace."""

    try:
        from claude_agent_sdk import ClaudeAgentOptions, query
    except ImportError as exc:
        raise RuntimeError(
            "claude-agent-sdk is not installed. Install requirements or run without --agent-sdk."
        ) from exc

    candidates_dir = project_root / "skills" / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)
    rule_id = f"rule_20260426_{cluster.cluster_id}"
    candidate_path = candidates_dir / f"{rule_id}.md"
    cluster_path = candidates_dir / f"{rule_id}_cluster.json"
    cluster_path.write_text(
        json.dumps(
            {
                "cluster_id": cluster.cluster_id,
                "trade_ids": cluster.trade_ids[:20],
                "summary": cluster.summary,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    system_prompt = dedent(
        """
        You are gsuda-engine's rule-drafting agent.

        Your only job is to convert clustered failed trades into one conservative,
        machine-checkable YAML+markdown suppression rule. Preserve provenance.
        Do not claim that Saju predicts stock prices. Frame Saju/Yi features as
        domain-informed categorical features that still require empirical validation.
        Preserve original Hanja notation when it appears in the cluster context.
        """
    ).strip()

    cluster_json = json.dumps(
        {
            "cluster_id": cluster.cluster_id,
            "trade_ids": cluster.trade_ids[:20],
            "summary": cluster.summary,
        },
        ensure_ascii=False,
        indent=2,
    )

    prompt = dedent(
        f"""
        Cluster summary JSON:
        {cluster_json}

        Draft exactly one candidate skill file.

        Requirements:
        - Start with YAML frontmatter delimited by ---
        - rule_id must be: {rule_id}
        - status must be: candidate
        - Use the trigger_conditions already recommended in the cluster summary.
        - Include spawned_from_failures from the provided trade IDs.
        - Include a domain_context section that shows the Hanja, romanized, and English pillar labels when provided.
        - Include placeholder backtest_stats with zeros/false; the validator will replace them.
        - After YAML, include a concise markdown explanation with "Why this rule exists" and "What it does".
        - Use ASCII punctuation only.
        - Output ONLY the markdown file content. Do not wrap it in a code block.
        """
    ).strip()

    options = ClaudeAgentOptions(
        allowed_tools=[],
        cwd=str(project_root),
        model=settings.claude_agent_model,
        max_turns=1,
        max_budget_usd=settings.agent_sdk_budget_usd,
        system_prompt=system_prompt,
    )

    chunks: list[str] = []
    async for message in query(prompt=prompt, options=options):
        if type(message).__name__ == "AssistantMessage":
            for block in getattr(message, "content", []):
                text = getattr(block, "text", None)
                if text:
                    chunks.append(text)
        if type(message).__name__ == "ResultMessage":
            cost = getattr(message, "total_cost_usd", None)
            turns = getattr(message, "num_turns", None)
            if cost is not None:
                print(f"  Claude Agent SDK usage: turns={turns}, estimated_cost_usd={cost:.4f}")

    rule_text = _strip_markdown_fence("\n".join(chunks).strip())
    if not rule_text.startswith("---\n"):
        raise RuntimeError("Claude Agent SDK returned invalid skill content; expected YAML frontmatter.")

    candidate_path.write_text(rule_text, encoding="utf-8")
    return rule_text


def _strip_markdown_fence(text: str) -> str:
    """Remove a surrounding markdown fence if a model adds one despite instructions."""

    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if len(lines) >= 3 and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return text
