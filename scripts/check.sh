#!/usr/bin/env bash
# Run a check tier and time each part:
#   bash scripts/check.sh quick   pytest -m "not slow" + Vitest            (per-step check, <= 60 s)
#   bash scripts/check.sh full    all pytest + npm test + all Playwright   (final check)
# Output is teed to tmp/check-<timestamp>.log; exits non-zero when any part fails.
# The step's own new test (e.g. one Playwright spec) is run next to this, not by it.
set -o pipefail
cd "$(dirname "$0")/.." || exit 1
tier=${1:-quick}
case $tier in quick|full) ;; *) echo "usage: $0 quick|full" >&2; exit 2 ;; esac
mkdir -p tmp
log=tmp/check-$(date +%Y%m%d-%H%M%S).log
PY=.venv/bin/python

names=() secs=() codes=()
part() {   # part <name> <command…>
  local name=$1; shift
  echo "== $name: $*"
  local t0=$(date +%s)
  "$@"
  local rc=$?
  names+=("$name"); secs+=($(( $(date +%s) - t0 ))); codes+=("$rc")
}

{
  if [ "$tier" = quick ]; then
    part pytest "$PY" -m pytest -q -m "not slow"
    part vitest bash -c 'cd web && npx vitest run'
  else
    part pytest "$PY" -m pytest -q
    part vitest bash -c 'cd web && npm test'
    part playwright bash -c 'cd web && npx playwright test --reporter=line'
  fi

  total=0 failed=0
  echo
  printf '%-12s %6s  %s\n' part seconds result
  for i in "${!names[@]}"; do
    total=$(( total + secs[i] ))
    [ "${codes[i]}" = 0 ] && r=ok || { r="FAILED (exit ${codes[i]})"; failed=1; }
    printf '%-12s %6s  %s\n' "${names[i]}" "${secs[i]}" "$r"
  done
  printf '%-12s %6s\n' total "$total"
  [ "$tier" = quick ] && [ "$total" -gt 60 ] && echo "WARNING: quick check took ${total} s (> 60 s)"
  echo "log: $log"
  exit $failed
} 2>&1 | tee "$log"
