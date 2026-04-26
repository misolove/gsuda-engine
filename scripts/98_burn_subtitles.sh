#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  printf "Usage: %s input_video output_video [subtitle_file]\n" "$0" >&2
  printf "Example: %s recordings/raw.mov recordings/subtitled.mp4 demo/demo_subtitles_final.srt\n" "$0" >&2
  exit 1
fi

INPUT_VIDEO="$1"
OUTPUT_VIDEO="$2"
SUBTITLE_FILE="${3:-demo/demo_subtitles_final.srt}"

if [[ ! -f "$INPUT_VIDEO" ]]; then
  printf "Input video not found: %s\n" "$INPUT_VIDEO" >&2
  exit 1
fi

if [[ ! -f "$SUBTITLE_FILE" ]]; then
  printf "Subtitle file not found: %s\n" "$SUBTITLE_FILE" >&2
  exit 1
fi

if ffmpeg -hide_banner -filters 2>/dev/null | grep -Eq '(^|[[:space:]])subtitles([[:space:]]|$)'; then
  ffmpeg -y \
    -i "$INPUT_VIDEO" \
    -vf "subtitles=filename=${SUBTITLE_FILE}:force_style=FontName=Arial\\,FontSize=20\\,Outline=2\\,Shadow=1\\,MarginV=36" \
    -c:a copy \
    "$OUTPUT_VIDEO"
else
  printf "ffmpeg subtitles filter is unavailable; attaching SRT as a soft subtitle track instead.\n" >&2
  ffmpeg -y \
    -i "$INPUT_VIDEO" \
    -i "$SUBTITLE_FILE" \
    -c:v copy \
    -c:a copy \
    -c:s mov_text \
    -metadata:s:s:0 language=eng \
    "$OUTPUT_VIDEO"
fi
