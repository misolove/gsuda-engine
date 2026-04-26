# gsuda-engine

Provenance-first self-evolving trading loop for Korean equities.

Claude drafts candidate risk rules from clustered failed trades, but every rule
must pass a validation gate before Risk Guardian loads it. The project combines
23 years of Korean securities-system experience with Saju/Yeokhak-inspired
feature engineering. The claim is not that Saju predicts stocks; the claim is
that domain-informed categorical features can be tested against market history.

## Saju Notation

Saju's native notation is Hanja, so the engine preserves it as provenance while
using English-first labels and compact validation keys for reproducible checks.
For example:

| Layer | Value |
| --- | --- |
| Primary English label | `Metal Goat` |
| Validation key | `MetalGoat` |
| Original Hanja | `辛未` |

Rules validate against the compact English key, while generated skill files keep
the English label and original Hanja in `domain_context` so judges can see the
native Saju structure without needing to read Chinese characters.

## Run The Demo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/03_run_loop.py
```

The default path is deterministic and does not require an API key. It produces:

- simulated recommendations with technical, year/month/day pillar, original
  Hanja provenance, solar-term, and hidden-stem proxy features
- T+5 outcome tagging
- two failure clusters
- one validated rule in `skills/active/`
- one rejected rule in `skills/quarantined/`

## Optional Claude Agent SDK Path

```bash
export ANTHROPIC_API_KEY=...
export CLAUDE_AGENT_MODEL=opus
python scripts/03_run_loop.py --agent-sdk
```

With `--agent-sdk`, Claude Agent SDK drafts candidate YAML+markdown skill
content and the local harness stores it under `skills/candidates/`. The
validator still controls deployment, so this is gated self-improvement rather
than autonomous self-modification.

## Judge Framing

The full local research warehouse covers Korean equities from 1995-05-02 to
2026-04-24: 11M+ enriched rows and 2,700+ stocks. The public demo is compact and
reproducible, while the validation design is built around 30-year historical
coverage and a 2024-2025 out-of-sample gate.

> Claude is creative; the validation gate is the judge.

## Submission Draft

See [SUBMISSION.md](SUBMISSION.md) for the hackathon form draft and demo script.
