# Hackathon Submission Draft

## Team Name

gsuda

## Team Members

HyuckJae Lee

## Project Name

gsuda-engine

## Selected Problem Statement

Build for what you know

## Public GitHub Repository

https://github.com/misolove/gsuda-engine

## Demo Video

TODO: Add YouTube unlisted URL after recording.

## Project Description

gsuda-engine is a provenance-first self-evolving trading loop for Korean equities.
It turns failed trade recommendations into auditable risk rules: trades are
logged with technical and Yeokhak-derived features, failures are clustered,
Claude drafts candidate suppression rules, and every rule must pass a validation
gate before Risk Guardian loads it.

The project comes from my own background: 23 years operating Korean securities
systems and 13 years studying Saju/Yeokhak. The claim is not that Saju predicts
stock prices. The claim is that domain-informed feature engineering can be
tested empirically inside a gated agentic workflow.

Saju's native notation is Hanja, so the engine preserves original pillar labels
such as `辛未` as provenance while making the English gloss, such as `Metal Goat`,
the judge-facing label. The validator uses compact English keys such as
`MetalGoat`, so judges can inspect the logic without prior Saju knowledge.

The public demo is compact and reproducible. The full local research warehouse
covers Korean equities from 1995-05-02 to 2026-04-24, with 11M+ enriched rows
and 2,700+ stocks. The validation design is built around this 30-year historical
coverage, with 2024-2025 used as an out-of-sample gate.

Claude is creative; the validation gate is the judge.

## Did You Use Claude Managed Agents? If So, How?

Yes. I used Claude Agent SDK as a bounded managed-agent workflow for the
rule-drafting step.

In the demo loop, `cluster_failures` identifies repeated failure patterns and
passes a structured failure-cluster summary to a Claude Agent SDK session. Claude
drafts candidate YAML+markdown skill content with trigger conditions,
provenance, and an explanation. The local harness stores the candidate under
`skills/candidates/`.

Claude does not deploy its own rule. `gsuda-engine` then runs a validation gate:
historical matches, cluster precision, winner damage, and a 2024-2025
out-of-sample check. Passing rules move to `skills/active/`; failing rules move
to `skills/quarantined/`.

This makes the agent loop auditable and gated rather than autonomous
self-modification.

## Thoughts And Feedback On Building With Opus 4.7

Opus 4.7 was strongest when the task required code, data reasoning, and unusual
domain context at the same time. It could work with Korean market features,
Saju/Yeokhak terminology, YAML rule formats, and validation logic without
flattening the project into generic trading advice.

The most useful workflow was to let Claude generate hypotheses and readable
candidate rules, then require market-history validation before deployment. That
separation made the system feel much safer: Claude is a strong rule drafter, but
the historical backtest remains the final authority.

## Demo Script

1. Open with the one-line pitch:

   "gsuda-engine is a self-evolving trading loop built from 23 years of Korean
   securities systems and 13 years of Yeokhak study. Claude drafts rules from
   failed trades, but no rule deploys without passing the validation gate."

   "The Saju layer preserves original Hanja notation, but the validator uses
   compact English keys so the system remains inspectable and reproducible."

2. Show the five-stage loop:

   - Stage 1: Trade fires
   - Stage 2: Outcome tracker
   - Stage 3: Cluster + Claude drafts rule
   - Stage 4: Backtest gate
   - Stage 5: Deployment

3. Run the paced, API-free recording script:

   ```bash
   ./scripts/99_record_demo.sh
   ```

4. Mention the optional Claude Agent SDK path:

   ```bash
   ./scripts/99_record_demo.sh --agent-sdk
   ```

5. Open the generated files:

   - `skills/candidates/rule_20260426_metalgoat_semis_midvol_not_last3.md`
   - `skills/active/rule_20260426_metalgoat_semis_midvol_not_last3.md`
   - `skills/quarantined/rule_20260426_highvol_lottery.md`

6. Close with the distinction:

   "This is not autonomous self-improvement. It is gated self-improvement:
   Claude drafts, provenance records why, and the validator decides."

## Demo Commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/03_run_loop.py
./scripts/99_record_demo.sh
```

Expected result:

```text
Found 2 failure clusters
[PASS] rule_20260426_metalgoat_semis_midvol_not_last3
[QUARANTINE] rule_20260426_highvol_lottery
Risk Guardian loaded 1 active rule
```
