# gsuda-engine

Provenance-first self-evolving trading loop for Korean equities.

Claude drafts candidate risk rules from clustered failed trades, but every rule
must pass a validation gate before Risk Guardian loads it. The project combines
23 years of Korean securities-system experience with Saju/Yeokhak-inspired
feature engineering. The claim is not that Saju predicts stocks; the claim is
that domain-informed categorical features can be tested against market history.

## What Problem It Solves

Trading agents can learn the wrong lesson from a few vivid failures. A language
model may draft a plausible new rule, but deploying that rule directly is
dangerous.

gsuda-engine makes the feedback loop explicit:

1. Log every recommendation with its full feature vector.
2. Wait for the realized outcome.
3. Cluster repeated failures.
4. Draft a candidate risk rule.
5. Promote the rule only if it passes historical validation.

The demo intentionally shows both outcomes: one rule is promoted to
`skills/active/`, and one tempting rule is sent to `skills/quarantined/` because
it would suppress too many winners.

## Saju/Yeokhak For Non-Korean Readers

Saju, also called the Four Pillars, is an East Asian calendrical classification
system. A birth time, or any timestamp, can be represented as pillars for year,
month, day, and hour. This MVP uses three pillars: year, month, and day.

Each pillar combines two ideas:

- a Heavenly Stem, often mapped to one of the Five Elements: Wood, Fire, Earth,
  Metal, Water
- an Earthly Branch, often mapped to an animal-like cycle label: Rat, Ox, Tiger,
  Goat, and so on

For example, the original Hanja pillar `辛未` is represented for judges as:

| Representation | Example | Why it exists |
| --- | --- | --- |
| English display label | `Metal Goat` | Readable for non-Korean judges |
| Compact validation key | `MetalGoat` | Stable for YAML, SQL, and rule matching |
| Original Hanja | `辛未` | Preserves the native Saju notation as provenance |

In this project, Saju is not used as an oracle. It is treated like a structured
categorical feature family, similar in spirit to sector, day-of-week, market
regime, or seasonality features. The only question the engine asks is empirical:
did this feature pattern repeatedly appear in failed trades, and does suppressing
that pattern survive validation?

The Yeokhak-inspired features are handled the same way. For example,
`jieqi_zone` approximates solar-term timing. Instead of assuming a market regime
changes instantly on a calendar boundary, the feature lets the validator test
whether behavior differs near the beginning, middle, or end of a solar-term
window. Hidden-stem proxy weights are also stored as numeric context, but they
do not become rules unless the backtest gate approves them.

## Concrete Rule Example

One active demo rule can be read in plain English:

> When the Strategy Orchestrator emits a Buy recommendation for a semiconductor
> stock, and the month pillar is `MetalGoat` (`辛未`, Metal Goat), and 20-day
> volatility is in a mid-range band, suppress the trade unless it is in the final
> three days of the solar-term window.

The important part is not that `Metal Goat` "predicts" the market. The important
part is provenance and validation:

- the rule traces back to a specific cluster of failed trades
- the original Saju label is preserved in the rule file
- the trigger conditions are machine-checkable
- the validator measures historical matches, cluster precision, winner damage,
  and 2024-2025 out-of-sample behavior
- only after passing those checks does the rule move to `skills/active/`

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

## Record The Demo

For a paced terminal recording without API latency:

```bash
./scripts/99_record_demo.sh
```

To record the live Claude Agent SDK path instead:

```bash
./scripts/99_record_demo.sh --agent-sdk
```

## Judge Framing

The full local research warehouse covers Korean equities from 1995-05-02 to
2026-04-24: 11M+ enriched rows and 2,700+ stocks. The public demo is compact and
reproducible, while the validation design is built around 30-year historical
coverage and a 2024-2025 out-of-sample gate.

> Claude is creative; the validation gate is the judge.

## Submission Draft

See [SUBMISSION.md](SUBMISSION.md) for the hackathon form draft and demo script.
