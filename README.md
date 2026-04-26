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

The ten Heavenly Stems are:

| # | Hanja | Korean | Romanization | Element | Polarity |
| --- | --- | --- | --- | --- | --- |
| 1 | `甲` | 갑 | Gap | Wood | Yang |
| 2 | `乙` | 을 | Eul | Wood | Yin |
| 3 | `丙` | 병 | Byeong | Fire | Yang |
| 4 | `丁` | 정 | Jeong | Fire | Yin |
| 5 | `戊` | 무 | Mu | Earth | Yang |
| 6 | `己` | 기 | Gi | Earth | Yin |
| 7 | `庚` | 경 | Gyeong | Metal | Yang |
| 8 | `辛` | 신 | Sin | Metal | Yin |
| 9 | `壬` | 임 | Im | Water | Yang |
| 10 | `癸` | 계 | Gye | Water | Yin |

The twelve Earthly Branches are:

| # | Hanja | Korean | Romanization | English label |
| --- | --- | --- | --- | --- |
| 1 | `子` | 자 | Ja | Rat |
| 2 | `丑` | 축 | Chuk | Ox |
| 3 | `寅` | 인 | In | Tiger |
| 4 | `卯` | 묘 | Myo | Rabbit |
| 5 | `辰` | 진 | Jin | Dragon |
| 6 | `巳` | 사 | Sa | Snake |
| 7 | `午` | 오 | O | Horse |
| 8 | `未` | 미 | Mi | Goat |
| 9 | `申` | 신 | Sin | Monkey |
| 10 | `酉` | 유 | Yu | Rooster |
| 11 | `戌` | 술 | Sul | Dog |
| 12 | `亥` | 해 | Hae | Pig |

The stems and branches advance together. Because one wheel has 10 positions and
the other has 12 positions, the combined cycle returns to the beginning after 60
steps. This is the sexagenary cycle, or 60-gapja (`六十甲子`).

```text
01 甲子 Wood Rat    -> 02 乙丑 Wood Ox      -> 03 丙寅 Fire Tiger
04 丁卯 Fire Rabbit -> 05 戊辰 Earth Dragon -> 06 己巳 Earth Snake
07 庚午 Metal Horse -> 08 辛未 Metal Goat   -> 09 壬申 Water Monkey
10 癸酉 Water Rooster
   -> 11 甲戌 Wood Dog -> ... -> 60 癸亥 Water Pig -> back to 01 甲子
```

In other words, `辛未` is not an arbitrary symbol. It is the eighth position in
a repeating 60-step calendar cycle: stem `辛` plus branch `未`, rendered in this
project as `Metal Goat`.

<details>
<summary>Full 60-gapja cycle used as categorical notation</summary>

| # | Hanja | English label | # | Hanja | English label |
| --- | --- | --- | --- | --- | --- |
| 01 | `甲子` | Wood Rat | 31 | `甲午` | Wood Horse |
| 02 | `乙丑` | Wood Ox | 32 | `乙未` | Wood Goat |
| 03 | `丙寅` | Fire Tiger | 33 | `丙申` | Fire Monkey |
| 04 | `丁卯` | Fire Rabbit | 34 | `丁酉` | Fire Rooster |
| 05 | `戊辰` | Earth Dragon | 35 | `戊戌` | Earth Dog |
| 06 | `己巳` | Earth Snake | 36 | `己亥` | Earth Pig |
| 07 | `庚午` | Metal Horse | 37 | `庚子` | Metal Rat |
| 08 | `辛未` | Metal Goat | 38 | `辛丑` | Metal Ox |
| 09 | `壬申` | Water Monkey | 39 | `壬寅` | Water Tiger |
| 10 | `癸酉` | Water Rooster | 40 | `癸卯` | Water Rabbit |
| 11 | `甲戌` | Wood Dog | 41 | `甲辰` | Wood Dragon |
| 12 | `乙亥` | Wood Pig | 42 | `乙巳` | Wood Snake |
| 13 | `丙子` | Fire Rat | 43 | `丙午` | Fire Horse |
| 14 | `丁丑` | Fire Ox | 44 | `丁未` | Fire Goat |
| 15 | `戊寅` | Earth Tiger | 45 | `戊申` | Earth Monkey |
| 16 | `己卯` | Earth Rabbit | 46 | `己酉` | Earth Rooster |
| 17 | `庚辰` | Metal Dragon | 47 | `庚戌` | Metal Dog |
| 18 | `辛巳` | Metal Snake | 48 | `辛亥` | Metal Pig |
| 19 | `壬午` | Water Horse | 49 | `壬子` | Water Rat |
| 20 | `癸未` | Water Goat | 50 | `癸丑` | Water Ox |
| 21 | `甲申` | Wood Monkey | 51 | `甲寅` | Wood Tiger |
| 22 | `乙酉` | Wood Rooster | 52 | `乙卯` | Wood Rabbit |
| 23 | `丙戌` | Fire Dog | 53 | `丙辰` | Fire Dragon |
| 24 | `丁亥` | Fire Pig | 54 | `丁巳` | Fire Snake |
| 25 | `戊子` | Earth Rat | 55 | `戊午` | Earth Horse |
| 26 | `己丑` | Earth Ox | 56 | `己未` | Earth Goat |
| 27 | `庚寅` | Metal Tiger | 57 | `庚申` | Metal Monkey |
| 28 | `辛卯` | Metal Rabbit | 58 | `辛酉` | Metal Rooster |
| 29 | `壬辰` | Water Dragon | 59 | `壬戌` | Water Dog |
| 30 | `癸巳` | Water Snake | 60 | `癸亥` | Water Pig |

</details>

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
