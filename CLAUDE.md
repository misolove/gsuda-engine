# gsuda-engine Claude Code Context

## Mission

Ship a working hackathon skeleton and CLI demo for `gsuda-engine`: a provenance-first, self-evolving trading agent loop for Korean equities.

The product claim is not that Saju predicts stock prices. The claim is that domain-informed feature engineering, including Korean Saju categorical features, can be used inside a gated trading-feedback system where AI-generated rules must pass empirical validation before deployment.

## Hackathon Frame

- Event: Built with Opus 4.7, a Claude Code Hackathon
- Owner: HyuckJae Lee / gsuda
- Submission target: 2026-04-27 09:00 KST
- UI target: terminal-only CLI demo
- MVP data mode: simulated historical replay, no broker integration

## Core Loop

1. Trade fires: Strategy Orchestrator emits a recommendation with a full feature vector and logs it to DuckDB.
2. Outcome tracker: T+5 / T+20 realized return tags wins, losses, and stop-outs.
3. Cluster + draft: failure cases are clustered, then Claude drafts suppression-rule skill files.
4. Backtest gate: candidate rules must pass historical-match, cluster-precision, winner-damage, and 2024-2025 out-of-sample checks.
5. Deployment: passing rules move to `skills/active/`; failed rules move to `skills/quarantined/`; Risk Guardian loads active rules on the next trade.

## MVP Scope

Build only:

- Daily-frequency simulated trades
- Three-pillar Saju categorical features with the hierarchy year -> month -> day
- Solar-term transition features such as `jieqi_zone`
- Hidden-stem proxy weights for the month pillar
- Local DuckDB at `data/gsuda.duckdb`
- One end-to-end CLI loop
- At least one active rule and one quarantined rule for the demo

Do not build:

- Web UI, Streamlit, dashboard, or frontend
- Live broker or KIS API integration
- Yijing / I Ching layer
- Weekly/monthly multi-scale logic
- Hermes bot or OpenClaw integration
- Production-grade orchestration

## Judge-Facing Language

Say:

- "Domain-informed feature engineering, validated by 30-year backtest"
- "Provenance-tracked AI: every rule traces back to failure cases"
- "Validation gate prevents blind deployment of AI-generated rules"
- "Gated self-improvement"

Do not say:

- "Saju predicts stock prices"
- "Fortune-telling for stocks"
- "AI evolves autonomously"

## Claude API Guardrails

- Do not call the Anthropic API before the rule-drafter phase.
- Use deterministic mock drafting by default so judges can run the repo without secrets.
- Use `python scripts/03_run_loop.py --agent-sdk` only when `ANTHROPIC_API_KEY` is present.
- The optional Agent SDK path lets Claude write candidate skill files in `skills/candidates/`.
- Track token usage when API calls are enabled.
- Pause before exceeding $30 of Claude API credits during build.

## Claude Managed-Agent Path

The default demo is reproducible without network or credentials. The optional
`--agent-sdk` path uses Claude Agent SDK as a bounded managed-agent workflow:

1. `cluster_failures` writes a structured failure-cluster summary.
2. Claude Agent SDK runs a bounded rule-drafting session.
3. The harness stores Claude's candidate YAML+markdown output in `skills/candidates/`.
4. `validator` decides active vs quarantined. The agent never deploys itself.

## Coding Style

- Keep the code small, readable, and demo-grade.
- Use English comments and docstrings.
- Prefer deterministic seeds for simulated data.
- Print clear stage banners in scripts for video recording.
- Keep Korean text UTF-8-safe in DB fields and markdown.
