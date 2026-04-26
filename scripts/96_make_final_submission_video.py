#!/usr/bin/env python3
"""Build the final 2+1 minute hard-captioned submission video.

Part 1 is a compressed, hard-captioned pitch generated from the repository
story. Part 2 reuses the earlier terminal recording as live execution evidence,
also with hard captions. The final MP4 is 1920x1080 and about three minutes.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PITCH_MODULE_PATH = ROOT / "scripts" / "97_make_pitch_video.py"
DEFAULT_TERMINAL_SOURCE = Path("/Users/letitbe/Desktop/2.mov")
DEFAULT_OUTPUT = ROOT / "demo" / "generated" / "gsuda_engine_final_2plus1_hardcoded.mp4"
DEFAULT_SRT = ROOT / "demo" / "generated" / "gsuda_engine_final_2plus1_hardcoded.srt"
DEFAULT_DESKTOP_COPY = Path("/Users/letitbe/Desktop/gsuda-engine-final-3min-hardcoded.mp4")
WIDTH = 1920
HEIGHT = 1080


def load_pitch_module():
    spec = importlib.util.spec_from_file_location("gsuda_pitch_video", PITCH_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load pitch generator: {PITCH_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PITCH = load_pitch_module()


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def srt_timestamp(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def write_srt(path: Path, captions: list[tuple[float, float, str]]) -> None:
    lines: list[str] = []
    for idx, (start, end, text) in enumerate(captions, start=1):
        lines.extend([str(idx), f"{srt_timestamp(start)} --> {srt_timestamp(end)}", text, ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def hard_caption_css() -> str:
    return """
.hard-caption {
  position: absolute;
  left: 112px;
  right: 112px;
  bottom: 108px;
  padding: 22px 30px;
  border-radius: 20px;
  background: rgba(5, 8, 13, 0.84);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: #fff9ed;
  font-size: 31px;
  line-height: 1.22;
  font-weight: 720;
  text-align: center;
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.36);
}
"""


def scene_html_with_caption(scene, idx: int, total: int) -> str:
    base = PITCH.scene_html(scene, idx, total)
    base = base.replace("</style>", hard_caption_css() + "</style>")
    caption = f'<div class="hard-caption">{html.escape(scene.srt_text)}</div>'
    return base.replace('<div class="footer">', caption + '\n    <div class="footer">')


def render_pitch_slides(chrome: Path, workdir: Path, scenes: list) -> list[Path]:
    html_dir = workdir / "pitch_html"
    raw_dir = workdir / "pitch_raw"
    png_dir = workdir / "pitch_png"
    html_dir.mkdir()
    raw_dir.mkdir()
    png_dir.mkdir()

    slide_paths: list[Path] = []
    total = len(scenes)
    for idx, scene in enumerate(scenes, start=1):
        html_path = html_dir / f"pitch_{idx:02d}.html"
        raw_path = raw_dir / f"pitch_{idx:02d}_raw.png"
        png_path = png_dir / f"pitch_{idx:02d}.png"
        html_path.write_text(scene_html_with_caption(scene, idx, total), encoding="utf-8")
        run(
            [
                str(chrome),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--allow-file-access-from-files",
                f"--window-size={WIDTH},{HEIGHT + 140}",
                f"--screenshot={raw_path}",
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
                str(raw_path),
                "-vf",
                f"crop={WIDTH}:{HEIGHT}:0:0",
                str(png_path),
            ]
        )
        slide_paths.append(png_path)
    return slide_paths


def render_caption_overlay(chrome: Path, workdir: Path, idx: int, text: str) -> Path:
    html_path = workdir / f"terminal_caption_{idx:02d}.html"
    raw_path = workdir / f"terminal_caption_{idx:02d}_raw.png"
    png_path = workdir / f"terminal_caption_{idx:02d}.png"
    safe_text = html.escape(text)
    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
html, body {{
  margin: 0;
  width: {WIDTH}px;
  height: {HEIGHT}px;
  background: transparent;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Helvetica Neue", Arial, sans-serif;
}}
.caption {{
  position: absolute;
  left: 104px;
  right: 104px;
  bottom: 58px;
  padding: 20px 28px;
  border-radius: 18px;
  background: rgba(3, 8, 13, 0.88);
  border: 1px solid rgba(110, 231, 183, 0.32);
  color: #fff9ed;
  font-size: 32px;
  line-height: 1.22;
  font-weight: 720;
  text-align: center;
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.42);
}}
</style>
</head>
<body>
  <div class="caption">{safe_text}</div>
</body>
</html>
"""
    html_path.write_text(html_doc, encoding="utf-8")
    run(
        [
            str(chrome),
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--default-background-color=00000000",
            "--window-size=1920,1080",
            f"--screenshot={raw_path}",
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
            str(raw_path),
            "-vf",
            f"crop={WIDTH}:{HEIGHT}:0:0",
            str(png_path),
        ]
    )
    return png_path


def build_pitch_scenes() -> list:
    # Scene indices come from scripts/97_make_pitch_video.py SCENES.
    selected = [
        (0, 8),
        (1, 10),
        (2, 12),
        (4, 12),
        (5, 13),
        (6, 12),
        (8, 11),
        (9, 12),
        (10, 12),
        (11, 10),
        (14, 8),
    ]
    scenes = [replace(PITCH.SCENES[idx], duration=duration) for idx, duration in selected]
    total = sum(scene.duration for scene in scenes)
    if abs(total - 120) > 0.01:
        raise AssertionError(f"Pitch scenes must total 120 seconds, got {total}")
    return scenes


def render_terminal_clip(
    source: Path,
    caption: Path,
    output: Path,
    start: float,
    duration: float,
) -> None:
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{duration:.3f}",
            "-i",
            str(source),
            "-loop",
            "1",
            "-t",
            f"{duration:.3f}",
            "-i",
            str(caption),
            "-f",
            "lavfi",
            "-t",
            f"{duration:.3f}",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-filter_complex",
            (
                f"[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[base];"
                "[1:v]format=rgba[cap];"
                "[base][cap]overlay=0:0:format=auto[v]"
            ),
            "-map",
            "[v]",
            "-map",
            "2:a",
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
            str(output),
        ]
    )


def concat_videos(inputs: list[Path], output: Path, workdir: Path) -> None:
    concat_path = workdir / "concat.ffconcat"
    concat_path.write_text(
        "ffconcat version 1.0\n" + "".join(f"file '{path.as_posix()}'\n" for path in inputs),
        encoding="utf-8",
    )
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


def make_video(output: Path, srt_path: Path, terminal_source: Path, desktop_copy: Path | None) -> None:
    if not terminal_source.exists():
        raise SystemExit(f"Terminal recording not found: {terminal_source}")

    chrome = PITCH.find_chrome(None)
    output.parent.mkdir(parents=True, exist_ok=True)
    srt_path.parent.mkdir(parents=True, exist_ok=True)

    pitch_scenes = build_pitch_scenes()
    terminal_segments = [
        (35, 12, "Live proof: the local script runs the closed loop from a clean repository."),
        (47, 12, "Failed trades become two candidate rules: one precise pattern and one tempting broad pattern."),
        (59, 12, "The validation gate promotes the Metal Goat rule and quarantines the unsafe high-volatility rule."),
        (71, 12, "The active skill preserves English labels, original Hanja, trigger conditions, and backtest stats."),
        (83, 12, "Risk Guardian loads only validated memory. Claude drafts; data validates; deployment is gated."),
    ]

    captions: list[tuple[float, float, str]] = []
    cursor = 0.0
    for scene in pitch_scenes:
        captions.append((cursor, cursor + scene.duration, scene.srt_text))
        cursor += scene.duration
    for _, duration, text in terminal_segments:
        captions.append((cursor, cursor + duration, text))
        cursor += duration
    write_srt(srt_path, captions)

    with tempfile.TemporaryDirectory(prefix="gsuda-final-video-") as tmp:
        workdir = Path(tmp)
        pitch_slides = render_pitch_slides(chrome, workdir, pitch_scenes)
        pitch_part = workdir / "part1_pitch_2min.mp4"
        pitch_workdir = workdir / "pitch_video"
        pitch_workdir.mkdir()
        PITCH.render_video(pitch_slides, pitch_scenes, pitch_part, pitch_workdir)

        terminal_clips: list[Path] = []
        caption_dir = workdir / "terminal_captions"
        caption_dir.mkdir()
        clips_dir = workdir / "terminal_clips"
        clips_dir.mkdir()
        for idx, (start, duration, text) in enumerate(terminal_segments, start=1):
            caption_png = render_caption_overlay(chrome, caption_dir, idx, text)
            clip_path = clips_dir / f"terminal_{idx:02d}.mp4"
            render_terminal_clip(terminal_source, caption_png, clip_path, start, duration)
            terminal_clips.append(clip_path)

        terminal_part = workdir / "part2_terminal_1min.mp4"
        concat_videos(terminal_clips, terminal_part, workdir)
        concat_videos([pitch_part, terminal_part], output, workdir)

    if desktop_copy:
        desktop_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, desktop_copy)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the final hard-captioned 2+1 minute submission video.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output MP4 path.")
    parser.add_argument("--srt", default=str(DEFAULT_SRT), help="Reference SRT transcript path.")
    parser.add_argument("--terminal-source", default=str(DEFAULT_TERMINAL_SOURCE), help="Earlier terminal recording to reuse for the final minute.")
    parser.add_argument("--desktop-copy", default=str(DEFAULT_DESKTOP_COPY), help="Optional convenience copy path; pass empty string to disable.")
    args = parser.parse_args()

    desktop_copy = Path(args.desktop_copy).resolve() if args.desktop_copy else None
    make_video(
        output=Path(args.output).resolve(),
        srt_path=Path(args.srt).resolve(),
        terminal_source=Path(args.terminal_source).resolve(),
        desktop_copy=desktop_copy,
    )
    print(f"Rendered {Path(args.output).resolve()}")
    print(f"Wrote transcript {Path(args.srt).resolve()}")
    if desktop_copy:
        print(f"Copied to {desktop_copy}")


if __name__ == "__main__":
    main()
