#!/bin/zsh
# Runs the exploratory follow-up of 12.11.2026 in order, cheapest first, and builds each report.
# Usage: scripts/run_followup.sh            (start now)
#        START=20:00 scripts/run_followup.sh  (wait until that time today, then start)
# Resumable: finished tasks are skipped, so run it again after an interruption.
# WORKERS (default 10) and WORKERS64 (default 5, for 64,000 training rows) set the parallel processes.
cd "$(dirname "$0")/.." || exit 1
LOG=results/followup.log
mkdir -p results
say() { echo "$(date '+%Y-%m-%dT%H:%M:%S') $*" | tee -a "$LOG"; }
if [[ -n "$START" ]]; then
  wait_s=$(( $(date -j -f '%H:%M' "$START" +%s) - $(date +%s) ))
  (( wait_s > 0 )) && { say "waiting until $START"; sleep "$wait_s"; }
fi
if pmset -g batt | grep -q "Battery Power"; then say "on battery power: not starting"; exit 1; fi
if [[ -n "$(git status --porcelain --untracked-files=no -- src uv.lock)" ]]; then
  say "uncommitted changes in src or uv.lock: not starting"; exit 1
fi
say "start at commit $(git rev-parse --short HEAD), ${WORKERS:-10} workers"
for e in content leaf mixed size draws synth sweep_size; do
  say "run $e"; caffeinate -is uv run dfx run "$e" --workers "${WORKERS:-10}" >> "$LOG" 2>&1 || say "FAILED tasks in $e"
  uv run dfx report "$e" --allow-incomplete >> "$LOG" 2>&1 || say "report $e FAILED"
done
say "run large"
caffeinate -is uv run dfx run large --folds 0,1,2 --workers "${WORKERS:-10}" >> "$LOG" 2>&1 || say "FAILED tasks in large"
uv run dfx report large --allow-incomplete >> "$LOG" 2>&1 || say "report large FAILED"
say "run large64"
caffeinate -is uv run dfx run large64 --folds 0,1,2 --workers "${WORKERS64:-5}" >> "$LOG" 2>&1 || say "FAILED tasks in large64"
uv run dfx report large64 --allow-incomplete >> "$LOG" 2>&1 || say "report large64 FAILED"
say "all done"
