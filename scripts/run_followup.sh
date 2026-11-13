#!/bin/zsh
# Runs the exploratory follow-up of 12-13.11.2026 (docs/followup.md) in order, cheapest first, and builds each report.
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
for e in large large_content sampling; do
  folds=(); [[ $e == sampling ]] || folds=(--folds 0,1,2)  # the large datasets run outer folds 0-2 only
  say "run $e"; caffeinate -is uv run dfx run "$e" $folds --workers "${WORKERS:-10}" >> "$LOG" 2>&1 || say "FAILED tasks in $e"
  uv run dfx report "$e" --allow-incomplete >> "$LOG" 2>&1 || say "report $e FAILED"
done
for e in large64 sampling_large sampling_large_sum; do  # the slow ones: 64,000 rows, or all columns at each split
  w=${WORKERS:-10}; [[ $e == large64 ]] && w=${WORKERS64:-5}
  say "run $e"; caffeinate -is uv run dfx run "$e" --folds 0,1,2 --workers "$w" >> "$LOG" 2>&1 || say "FAILED tasks in $e"
  uv run dfx report "$e" --allow-incomplete >> "$LOG" 2>&1 || say "report $e FAILED"
done
uv run python scripts/followup_report.py > /dev/null || say "followup_report FAILED"
say "all done"
