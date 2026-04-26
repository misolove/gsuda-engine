#!/usr/bin/env python3
"""Render a polished, silent 3-minute pitch video from local repo context.

The script uses Google Chrome headless to render HTML slides to PNG, then ffmpeg
to assemble those stills into an MP4 with a silent audio track. It avoids paid
API calls and keeps the result deterministic for a late-stage hackathon submit.
"""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "demo" / "generated" / "gsuda_engine_pitch_video.mp4"
DEFAULT_SRT = ROOT / "demo" / "generated" / "gsuda_engine_pitch_video.srt"
CHROME_CANDIDATES = [
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
]
WIDTH = 1920
HEIGHT = 1080


@dataclass(frozen=True)
class Scene:
    duration: float
    headline: str
    subtitle: str
    html_body: str
    srt_text: str
    theme: str = "default"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def pills(items: list[str]) -> str:
    return "".join(f"<span class='pill'>{esc(item)}</span>" for item in items)


def bullets(items: list[str]) -> str:
    return "<ul class='bullets'>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def metric_cards(items: list[tuple[str, str, str]]) -> str:
    return (
        "<div class='metric-grid'>"
        + "".join(
            "<div class='metric-card'>"
            f"<div class='metric-value'>{esc(value)}</div>"
            f"<div class='metric-label'>{esc(label)}</div>"
            f"<div class='metric-note'>{esc(note)}</div>"
            "</div>"
            for value, label, note in items
        )
        + "</div>"
    )


def loop_diagram() -> str:
    stages = [
        ("1", "Trade fires", "full feature vector"),
        ("2", "Outcome tracker", "T+5 / T+20 result"),
        ("3", "Cluster failures", "Claude drafts rule"),
        ("4", "Backtest gate", "four validation checks"),
        ("5", "Deployment", "Risk Guardian loads"),
    ]
    return (
        "<div class='loop'>"
        + "".join(
            "<div class='loop-node'>"
            f"<div class='loop-num'>{num}</div>"
            f"<div class='loop-title'>{esc(title)}</div>"
            f"<div class='loop-copy'>{esc(copy)}</div>"
            "</div>"
            for num, title, copy in stages
        )
        + "</div>"
    )


def layer_table() -> str:
    rows = [
        ("Year", "年柱", "macro time climate", "year_pillar x meridian_branch"),
        ("Month", "月柱", "seasonal + solar-term climate", "month_pillar x jieqi_zone"),
        ("Day", "日柱", "decision-day climate", "day_pillar x meridian_branch"),
        ("Hour", "子午流注", "active meridian channel", "meridian_branch"),
    ]
    return (
        "<table class='clean-table'>"
        "<tr><th>Layer</th><th>Hanja</th><th>Role</th><th>Feature</th></tr>"
        + "".join(
            "<tr>"
            f"<td>{esc(layer)}</td><td class='hanja'>{esc(hanja)}</td>"
            f"<td>{esc(role)}</td><td><code>{esc(feature)}</code></td>"
            "</tr>"
            for layer, hanja, role, feature in rows
        )
        + "</table>"
    )


def meridian_table() -> str:
    rows = [
        ("子", "23-01", "Gallbladder", "decision / risk initiation"),
        ("巳", "09-11", "Spleen", "assimilation / news digestion"),
        ("午", "11-13", "Heart", "attention / sentiment expression"),
        ("申", "15-17", "Bladder", "pressure / close-time risk release"),
    ]
    return (
        "<table class='clean-table compact'>"
        "<tr><th>Branch</th><th>Window</th><th>Meridian</th><th>Market analogy</th></tr>"
        + "".join(
            "<tr>"
            f"<td class='hanja'>{esc(branch)}</td><td>{esc(window)}</td>"
            f"<td>{esc(meridian)}</td><td>{esc(analogy)}</td>"
            "</tr>"
            for branch, window, meridian, analogy in rows
        )
        + "</table>"
    )


def saju_cycle() -> str:
    return (
        "<div class='cycle-row'>"
        "<div class='cycle-card'><span class='hanja big'>甲子</span><span>Wood Rat</span></div>"
        "<div class='arrow'>→</div>"
        "<div class='cycle-card'><span class='hanja big'>乙丑</span><span>Wood Ox</span></div>"
        "<div class='arrow'>→</div>"
        "<div class='cycle-card active'><span class='hanja big'>辛未</span><span>Metal Goat</span></div>"
        "<div class='arrow'>→</div>"
        "<div class='cycle-card'><span class='hanja big'>癸亥</span><span>Water Pig</span></div>"
        "</div>"
        "<p class='support'>Hanja is preserved as provenance. English labels are used for judges and validation keys.</p>"
    )


def terminal_block(lines: list[str]) -> str:
    return (
        "<div class='terminal'>"
        + "".join(f"<div>{line}</div>" for line in lines)
        + "</div>"
    )


SCENES = [
    Scene(
        9,
        "gsuda-engine",
        "Provenance-first self-evolving trading loop",
        "<div class='hero-line'>Claude drafts.<br>Data validates.<br><span>Risk Guardian deploys.</span></div>"
        + pills(["Korean equities", "Saju / Yeokhak features", "validation-gated AI"]),
        "gsuda-engine is a provenance-first self-evolving trading loop. Claude drafts. Data validates. Risk Guardian deploys.",
        "hero",
    ),
    Scene(
        10,
        "The Problem",
        "Trading agents can learn the wrong lesson.",
        bullets(
            [
                "A few vivid losses can produce a plausible but dangerous new rule.",
                "An LLM can draft that rule faster than a human.",
                "But direct deployment is how self-improvement becomes self-damage.",
            ]
        ),
        "Trading agents can learn the wrong lesson from a few vivid losses. The project adds a validation gate before any AI-drafted rule can deploy.",
    ),
    Scene(
        12,
        "Closed Loop",
        "Every rule must trace back to the failures that created it.",
        loop_diagram(),
        "The loop logs trades, tracks outcomes, clusters failures, drafts candidate rules, validates them, and only then deploys through Risk Guardian.",
    ),
    Scene(
        12,
        "Demo Evidence",
        "The API-free path runs end-to-end from a clean clone.",
        metric_cards(
            [
                ("178", "simulated recommendations", "full technical + Saju feature vectors"),
                ("2", "failure clusters", "one strong, one tempting but unsafe"),
                ("1 / 1", "active / quarantined", "both outcomes visible for judges"),
            ]
        ),
        "The demo logs 178 simulated recommendations, finds two failure clusters, promotes one rule, and quarantines one unsafe rule.",
    ),
    Scene(
        12,
        "Validation Gate",
        "Claude is creative. The gate is the judge.",
        terminal_block(
            [
                "<span class='ok'>[PASS]</span> historical_matches=75",
                "<span class='ok'>[PASS]</span> cluster_precision=0.9467",
                "<span class='ok'>[PASS]</span> winner_damage_pct=5.33",
                "<span class='warn'>[QUARANTINE]</span> winner_damage_pct=40.0",
            ]
        ),
        "The promoted rule passes historical matches, cluster precision, winner damage, and out-of-sample checks. The broad high-volatility rule is quarantined.",
    ),
    Scene(
        13,
        "What Only I Would Build",
        "23 years of Korean securities systems + 13 years of Saju study.",
        bullets(
            [
                "The claim is not that Saju predicts stocks.",
                "The claim is that domain-informed calendar features can be tested.",
                "Every unusual idea must become a logged feature and survive validation.",
            ]
        ),
        "This is built from 23 years of Korean securities-system experience and 13 years of Saju and Yeokhak study. It is empirical, not fortune-telling.",
    ),
    Scene(
        13,
        "Time Climate",
        "Year, month, and day pillars become behavioral context.",
        "<div class='formula'>year climate + month climate + day climate<br><span>→ collective attention, risk appetite, narrative timing</span></div>"
        + pills(["年柱 year", "月柱 month", "日柱 day"]),
        "The research thesis is time climate: if many participants share the same temporal context, it may nudge attention, risk appetite, and narrative timing.",
    ),
    Scene(
        11,
        "Assets Have A Market Life",
        "A stock or token is not just a price series.",
        "<div class='life-row'>"
        "<div>birth<br><span>listing</span></div>"
        "<div>growth<br><span>liquidity</span></div>"
        "<div>maturity<br><span>crowding</span></div>"
        "<div>dormancy<br><span>fading volume</span></div>"
        "<div>rebirth<br><span>new theme</span></div>"
        "</div>",
        "An investment target can be studied like a living market object, with an origin timestamp, lifecycle, and exposure to year, month, and day climates.",
    ),
    Scene(
        13,
        "Saju Notation",
        "Native symbols remain visible. Validation stays machine-checkable.",
        saju_cycle(),
        "The engine preserves original Hanja such as Shin-Mi, Metal Goat, while using English labels and compact validation keys for reproducible checks.",
    ),
    Scene(
        14,
        "Meridian Time",
        "A traditional model for time, attention, and rhythm.",
        meridian_table()
        + "<p class='support'>No medical claims. This is a cultural timing model translated into testable market features.</p>",
        "The meridian clock maps two-hour windows to traditional human-function themes. gsuda-engine treats this as a feature hypothesis, not a medical or predictive claim.",
    ),
    Scene(
        14,
        "Layered Meridian Effects",
        "The hour is interpreted inside year and month climate.",
        layer_table(),
        "A meridian window is not a standalone lookup. Year pillar, month pillar, solar-term zone, day pillar, and hour window become interaction features.",
    ),
    Scene(
        13,
        "Historical Grounding",
        "The local research warehouse spans 1995 to 2026.",
        metric_cards(
            [
                ("30 yrs", "Korean equity history", "1995-05-02 to 2026-04-24"),
                ("11M+", "enriched rows", "technical + calendar features"),
                ("2024-2025", "out-of-sample gate", "rules must hold beyond the cluster"),
            ]
        ),
        "The local research warehouse spans Korean equities from 1995 to 2026 with more than 11 million enriched rows and an out-of-sample gate for 2024 to 2025.",
    ),
    Scene(
        12,
        "Rule Provenance",
        "The active rule is readable and auditable.",
        terminal_block(
            [
                "rule_id: rule_20260426_metalgoat_semis_midvol_not_last3",
                "month_pillar: MetalGoat",
                "original_hanja: 辛未",
                "status: active",
            ]
        ),
        "The active rule keeps its source failures, trigger conditions, backtest statistics, English label, and original Hanja provenance.",
    ),
    Scene(
        10,
        "Why The Quarantine Matters",
        "The rejected rule looked plausible, but damaged too many winners.",
        terminal_block(
            [
                "rule_id: rule_20260426_highvol_lottery",
                "historical_matches: 60",
                "winner_damage_pct: 40.0",
                "<span class='warn'>failure_reason: winner_damage_gt_35pct</span>",
            ]
        ),
        "The quarantined rule is the safety story. It matched failures, but it would have suppressed too many winners, so it was blocked.",
    ),
    Scene(
        12,
        "Built With Opus 4.7",
        "Gated self-improvement, not autonomous self-modification.",
        "<div class='closing'>Claude drafts candidate behavioral memory.<br>DuckDB validation decides.<br>Risk Guardian loads only what passes.</div>"
        + "<div class='repo'>github.com/misolove/gsuda-engine</div>",
        "Built with Opus 4.7 for gated self-improvement. Claude drafts candidate behavioral memory. DuckDB validation decides. Risk Guardian loads only what passes.",
        "hero",
    ),
]


CSS = f"""
@page {{ size: {WIDTH}px {HEIGHT}px; margin: 0; }}
* {{ box-sizing: border-box; }}
html {{
  margin: 0;
  width: {WIDTH}px;
  height: {HEIGHT}px;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 12%, rgba(110, 231, 183, 0.12), transparent 32%),
    radial-gradient(circle at 82% 84%, rgba(251, 191, 36, 0.10), transparent 35%),
    linear-gradient(135deg, #0a0f1f 0%, #141414 50%, #1f1710 100%);
}}
body {{
  margin: 0;
  width: {WIDTH}px;
  height: {HEIGHT}px;
  overflow: hidden;
  background: transparent;
  color: #f6f3ea;
  font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Helvetica Neue", Arial, sans-serif;
}}
.frame {{
  position: relative;
  width: 100%;
  height: {HEIGHT}px;
  padding: 78px 96px 66px;
}}
.frame::before {{
  content: "";
  position: absolute;
  inset: 32px;
  border: 1px solid rgba(246, 243, 234, 0.11);
  pointer-events: none;
}}
.frame::after {{
  content: "";
  position: absolute;
  left: 96px;
  right: 96px;
  bottom: 46px;
  height: 4px;
  background: linear-gradient(90deg, #6ee7b7, #fbbf24, #fb7185);
  opacity: 0.75;
}}
.kicker {{
  color: #6ee7b7;
  font-size: 28px;
  font-weight: 760;
  letter-spacing: 0;
  margin-bottom: 20px;
}}
h1 {{
  margin: 0;
  max-width: 1540px;
  font-size: 84px;
  line-height: 0.98;
  letter-spacing: 0;
}}
.subtitle {{
  margin-top: 28px;
  color: #d8d3c8;
  max-width: 1480px;
  font-size: 38px;
  line-height: 1.18;
}}
.content {{
  margin-top: 60px;
}}
.hero h1 {{
  font-size: 120px;
}}
.hero .subtitle {{
  font-size: 44px;
}}
.hero-line {{
  margin-top: 72px;
  font-size: 74px;
  line-height: 1.12;
  font-weight: 780;
}}
.hero-line span, .closing span {{
  color: #fbbf24;
}}
.pill {{
  display: inline-flex;
  align-items: center;
  margin: 46px 16px 0 0;
  padding: 18px 24px;
  border: 1px solid rgba(110, 231, 183, 0.34);
  color: #e8fff7;
  background: rgba(110, 231, 183, 0.10);
  font-size: 26px;
  border-radius: 999px;
}}
.bullets {{
  margin: 0;
  padding: 0;
  list-style: none;
  max-width: 1460px;
}}
.bullets li {{
  margin: 24px 0;
  padding-left: 46px;
  position: relative;
  font-size: 42px;
  line-height: 1.22;
  color: #f8f6ef;
}}
.bullets li::before {{
  content: "";
  position: absolute;
  left: 0;
  top: 18px;
  width: 18px;
  height: 18px;
  background: #fbbf24;
  border-radius: 50%;
}}
.loop {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 22px;
}}
.loop-node {{
  min-height: 350px;
  padding: 30px 24px;
  background: rgba(255, 255, 255, 0.075);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 22px;
}}
.loop-num {{
  width: 64px;
  height: 64px;
  display: grid;
  place-items: center;
  background: #6ee7b7;
  color: #071017;
  border-radius: 50%;
  font-weight: 900;
  font-size: 36px;
}}
.loop-title {{
  margin-top: 34px;
  font-size: 35px;
  line-height: 1.05;
  font-weight: 820;
}}
.loop-copy {{
  margin-top: 18px;
  color: #d8d3c8;
  font-size: 26px;
  line-height: 1.25;
}}
.metric-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}}
.metric-card {{
  min-height: 330px;
  padding: 36px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 24px;
}}
.metric-value {{
  color: #fbbf24;
  font-size: 88px;
  font-weight: 900;
  line-height: 1;
}}
.metric-label {{
  margin-top: 22px;
  font-size: 34px;
  font-weight: 760;
}}
.metric-note {{
  margin-top: 16px;
  color: #d8d3c8;
  font-size: 25px;
  line-height: 1.25;
}}
.terminal {{
  max-width: 1450px;
  padding: 34px 38px;
  background: #090d12;
  border: 1px solid rgba(110, 231, 183, 0.22);
  border-radius: 20px;
  box-shadow: 0 18px 70px rgba(0, 0, 0, 0.32);
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 31px;
  line-height: 1.48;
  color: #e9f0e7;
}}
.terminal div::before {{
  content: "$ ";
  color: #6ee7b7;
}}
.ok {{
  color: #6ee7b7;
}}
.warn {{
  color: #fbbf24;
}}
.formula {{
  max-width: 1500px;
  padding: 48px;
  background: rgba(255, 255, 255, 0.08);
  border-left: 9px solid #fb7185;
  border-radius: 18px;
  font-size: 55px;
  line-height: 1.22;
  font-weight: 780;
}}
.formula span {{
  color: #d8d3c8;
  font-size: 42px;
  font-weight: 650;
}}
.life-row {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 22px;
}}
.life-row div {{
  min-height: 270px;
  padding: 34px 24px;
  background: rgba(255, 255, 255, 0.08);
  border-top: 7px solid #6ee7b7;
  border-radius: 20px;
  text-align: center;
  font-size: 39px;
  font-weight: 820;
}}
.life-row span {{
  display: block;
  margin-top: 18px;
  color: #d8d3c8;
  font-size: 25px;
  font-weight: 560;
}}
.cycle-row {{
  display: grid;
  grid-template-columns: 1fr 70px 1fr 70px 1.2fr 70px 1fr;
  gap: 16px;
  align-items: center;
}}
.cycle-card {{
  min-height: 230px;
  display: grid;
  place-items: center;
  gap: 10px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 22px;
  font-size: 30px;
}}
.cycle-card.active {{
  background: rgba(251, 191, 36, 0.14);
  border-color: rgba(251, 191, 36, 0.55);
}}
.hanja {{
  font-family: "Apple SD Gothic Neo", "Hiragino Sans", "PingFang SC", sans-serif;
}}
.big {{
  font-size: 78px;
  font-weight: 800;
}}
.arrow {{
  color: #6ee7b7;
  text-align: center;
  font-size: 58px;
  font-weight: 700;
}}
.support {{
  margin-top: 34px;
  color: #d8d3c8;
  font-size: 32px;
  line-height: 1.25;
}}
.clean-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 30px;
  overflow: hidden;
  border-radius: 20px;
}}
.clean-table th {{
  background: rgba(110, 231, 183, 0.18);
  color: #effff8;
  text-align: left;
  padding: 22px 24px;
  font-size: 26px;
}}
.clean-table td {{
  padding: 22px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.07);
}}
.clean-table.compact td {{
  font-size: 32px;
}}
code {{
  color: #fbbf24;
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 25px;
}}
.closing {{
  max-width: 1540px;
  font-size: 60px;
  line-height: 1.22;
  font-weight: 800;
}}
.repo {{
  position: absolute;
  left: 96px;
  bottom: 92px;
  color: #6ee7b7;
  font-size: 34px;
  font-weight: 760;
}}
.footer {{
  position: absolute;
  right: 96px;
  bottom: 92px;
  color: rgba(246, 243, 234, 0.62);
  font-size: 24px;
}}
"""


def scene_html(scene: Scene, idx: int, total: int) -> str:
    title = esc(scene.headline)
    subtitle = esc(scene.subtitle)
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>{CSS}</style>
</head>
<body>
  <main class="frame {scene.theme}">
    <div class="kicker">gsuda-engine · hackathon submission</div>
    <h1>{title}</h1>
    <div class="subtitle">{subtitle}</div>
    <section class="content">{scene.html_body}</section>
    <div class="footer">{idx:02d} / {total:02d}</div>
  </main>
</body>
</html>
"""


def srt_timestamp(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def write_srt(path: Path, scenes: list[Scene]) -> None:
    lines: list[str] = []
    cursor = 0.0
    for idx, scene in enumerate(scenes, start=1):
        start = cursor
        end = cursor + scene.duration
        lines.extend(
            [
                str(idx),
                f"{srt_timestamp(start)} --> {srt_timestamp(end)}",
                scene.srt_text,
                "",
            ]
        )
        cursor = end
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def find_chrome(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if path.exists():
            return path
        raise SystemExit(f"Chrome executable not found: {path}")
    for path in CHROME_CANDIDATES:
        if path.exists():
            return path
    discovered = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
    if discovered:
        return Path(discovered)
    raise SystemExit("Google Chrome or Chromium is required for headless slide rendering.")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def render_slides(chrome: Path, workdir: Path, scenes: list[Scene]) -> list[Path]:
    slide_paths: list[Path] = []
    total = len(scenes)
    html_dir = workdir / "html"
    png_dir = workdir / "png"
    html_dir.mkdir()
    png_dir.mkdir()
    for idx, scene in enumerate(scenes, start=1):
        html_path = html_dir / f"slide_{idx:02d}.html"
        raw_png_path = png_dir / f"slide_{idx:02d}_raw.png"
        png_path = png_dir / f"slide_{idx:02d}.png"
        html_path.write_text(scene_html(scene, idx, total), encoding="utf-8")
        run(
            [
                str(chrome),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--allow-file-access-from-files",
                f"--window-size={WIDTH},{HEIGHT + 140}",
                f"--screenshot={raw_png_path}",
                html_path.as_uri(),
            ]
        )
        run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(raw_png_path),
                "-vf",
                f"crop={WIDTH}:{HEIGHT}:0:0",
                str(png_path),
            ]
        )
        raw_png_path.unlink(missing_ok=True)
        slide_paths.append(png_path)
    return slide_paths


def render_video(slides: list[Path], scenes: list[Scene], output: Path, workdir: Path) -> None:
    clips_dir = workdir / "clips"
    clips_dir.mkdir()
    clip_paths: list[Path] = []
    for idx, (slide, scene) in enumerate(zip(slides, scenes, strict=True), start=1):
        clip_path = clips_dir / f"clip_{idx:02d}.mp4"
        run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-loop",
                "1",
                "-t",
                f"{scene.duration:.3f}",
                "-i",
                str(slide),
                "-f",
                "lavfi",
                "-t",
                f"{scene.duration:.3f}",
                "-i",
                "anullsrc=channel_layout=stereo:sample_rate=48000",
                "-vf",
                f"scale={WIDTH}:{HEIGHT},format=yuv420p",
                "-r",
                "30",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-shortest",
                str(clip_path),
            ]
        )
        clip_paths.append(clip_path)

    concat_path = workdir / "clips.ffconcat"
    concat_path.write_text(
        "ffconcat version 1.0\n"
        + "".join(f"file '{clip.as_posix()}'\n" for clip in clip_paths),
        encoding="utf-8",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the gsuda-engine pitch video.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output MP4 path.")
    parser.add_argument("--srt", default=str(DEFAULT_SRT), help="Output SRT path.")
    parser.add_argument("--chrome", default=None, help="Optional Chrome/Chromium executable path.")
    parser.add_argument("--keep-frames", action="store_true", help="Copy rendered PNG frames beside the output.")
    args = parser.parse_args()

    chrome = find_chrome(args.chrome)
    output = Path(args.output).resolve()
    srt_path = Path(args.srt).resolve()

    write_srt(srt_path, SCENES)
    with tempfile.TemporaryDirectory(prefix="gsuda-pitch-video-") as tmp:
        workdir = Path(tmp)
        slides = render_slides(chrome, workdir, SCENES)
        render_video(slides, SCENES, output, workdir)
        if args.keep_frames:
            frames_dir = output.parent / "frames"
            frames_dir.mkdir(parents=True, exist_ok=True)
            for slide in slides:
                shutil.copy2(slide, frames_dir / slide.name)

    duration = sum(scene.duration for scene in SCENES)
    print(f"Rendered {output}")
    print(f"Wrote subtitles {srt_path}")
    print(f"Duration: {duration:.1f}s")


if __name__ == "__main__":
    main()
