# gsuda-engine Demo Voiceover

## 0:00-0:25 Opening

Hi, I am HyuckJae Lee, also known as gsuda.

This is gsuda-engine: a provenance-first self-evolving trading loop for Korean equities.

Claude drafts. Data validates. Risk Guardian deploys.

## 0:25-0:55 What Makes It Mine

The project comes from my own background: 23 years operating Korean securities systems, and 13 years studying Saju and Yeokhak.

The claim is not that Saju predicts stock prices. The claim is that domain-informed categorical features can be tested empirically against market history.

## 0:55-2:15 Live Run

This command runs the full closed loop.

Stage 1 logs simulated recommendations with technical indicators, year, month, and day pillars, original Hanja provenance, solar-term timing, and hidden-stem proxy weights.

Stage 2 tags T+5 outcomes.

Stage 3 clusters failures and uses Claude Agent SDK to draft candidate YAML and markdown skill files.

Stage 4 runs the validation gate.

Stage 5 deploys only validated rules to Risk Guardian.

Here we have one promoted rule and one quarantined rule.

## 2:15-3:10 Active Rule

This is the promoted rule.

The judge-facing label is English: Metal Goat.

The compact validation key is MetalGoat.

The original Hanja, 辛未, is preserved as domain provenance.

The rule also records the failed trade IDs, trigger conditions, and backtest statistics.

## 3:10-3:55 Quarantined Rule

This rule was rejected by the validation gate.

It matched enough historical cases, but winner damage was too high.

That is the key design principle: this is gated self-improvement, not autonomous self-modification.

## 3:55-4:40 README And Context

The public demo is compact and reproducible.

The broader local research warehouse covers Korean equities from 1995 to 2026, with more than 11 million enriched rows and more than 2,700 stocks.

The demo packages the core validation loop so judges can run it without private infrastructure.

## 4:40-5:00 Closing

gsuda-engine turns trading failures into validated behavioral memory.

Claude drafts. Data validates. Risk Guardian deploys.
