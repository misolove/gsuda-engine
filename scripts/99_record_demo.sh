#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SHORT_PAUSE="${DEMO_SHORT_PAUSE:-5}"
MEDIUM_PAUSE="${DEMO_MEDIUM_PAUSE:-15}"
LONG_PAUSE="${DEMO_LONG_PAUSE:-35}"
RUN_MODE="${1:---mock}"
PYTHON_BIN="${PYTHON_BIN:-python}"

case "$RUN_MODE" in
  --mock)
    RUN_ARGS=()
    DRAFTING_LINE="This recording uses the deterministic API-free drafter for speed and reliability."
    ;;
  --agent-sdk)
    RUN_ARGS=("--agent-sdk")
    DRAFTING_LINE="This recording uses Claude Agent SDK to draft candidate skill files."
    ;;
  *)
    printf "Usage: %s [--mock|--agent-sdk]\n" "$0" >&2
    exit 1
    ;;
esac

banner() {
  local title="$1"
  printf "\n"
  printf "%s\n" "========================================================================"
  printf "%s\n" "$title"
  printf "%s\n" "========================================================================"
}

pause_for_recording() {
  local seconds="$1"
  printf "\n[Recording pause: %s seconds]\n" "$seconds"
  sleep "$seconds"
}

show_command() {
  printf "\n$ %s\n" "$*"
}

show_excerpt() {
  local title="$1"
  local file="$2"
  local start_line="$3"
  local end_line="$4"

  banner "$title"
  show_command "sed -n '${start_line},${end_line}p' $file"
  sed -n "${start_line},${end_line}p" "$file"
  pause_for_recording "$LONG_PAUSE"
}

if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
  PYTHON_BIN="${PYTHON_BIN:-python}"
fi

if [[ "${RUN_ARGS[*]:-}" == "--agent-sdk" ]]; then
  if [[ -z "${ANTHROPIC_API_KEY:-}" || "${ANTHROPIC_API_KEY}" == "your_api_key_here" ]]; then
    printf "ANTHROPIC_API_KEY is missing or still uses the placeholder.\n" >&2
    printf "Use --mock for an API-free recording, or restore .env before recording.\n" >&2
    exit 1
  fi
fi

clear
banner "gsuda-engine recording script"
cat <<TEXT
This recording script is intentionally paced for a 4-5 minute demo.

Story:
1. Candidate risk rules are drafted from clustered failures.
2. The validator decides: one rule is promoted, one is quarantined.
3. Saju notation is English-first for judges, with original Hanja preserved.

${DRAFTING_LINE}

Opening line:
"Claude drafts. Data validates. Risk Guardian deploys."
TEXT
pause_for_recording "$LONG_PAUSE"

clear
banner "Live demo: run the complete closed loop"
if ((${#RUN_ARGS[@]})); then
  show_command "$PYTHON_BIN scripts/03_run_loop.py ${RUN_ARGS[*]}"
else
  show_command "$PYTHON_BIN scripts/03_run_loop.py"
fi
pause_for_recording "$SHORT_PAUSE"
if ((${#RUN_ARGS[@]})); then
  "$PYTHON_BIN" scripts/03_run_loop.py "${RUN_ARGS[@]}"
else
  "$PYTHON_BIN" scripts/03_run_loop.py
fi
pause_for_recording "$LONG_PAUSE"

show_excerpt \
  "Promoted active rule: English gloss plus original Hanja provenance" \
  "skills/active/rule_20260426_metalgoat_semis_midvol_not_last3.md" \
  1 \
  110

show_excerpt \
  "Quarantined rule: validation gate prevents winner damage" \
  "skills/quarantined/rule_20260426_highvol_lottery.md" \
  1 \
  120

show_excerpt \
  "README: judge-facing framing and 30-year historical context" \
  "README.md" \
  1 \
  70

banner "Closing"
cat <<'TEXT'
Closing line:
"gsuda-engine turns trading failures into validated behavioral memory.
Claude drafts. Data validates. Risk Guardian deploys."

Recording sequence complete.
TEXT
pause_for_recording "$MEDIUM_PAUSE"
