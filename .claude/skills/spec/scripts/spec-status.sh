#!/usr/bin/env bash
# Print one line per open change: name · status · done/total steps · reviewed · next step.
# The same rules the status pane uses. Run from the repo root.
set -euo pipefail
dir="specs/changes"
[[ -d "$dir" ]] || { echo "no changes (no $dir)"; exit 0; }
found=0
for c in "$dir"/*/; do
  [[ -d "$c" ]] || continue
  found=1
  name=$(basename "$c")
  status=$(grep -h '^status:' "$c"/*.md 2>/dev/null | sed 's/^status: *//' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
  done_n=0; total=0
  if [[ -f "$c/plan.md" ]]; then
    done_n=$(grep -c -E '^\s*- \[x\]' "$c/plan.md" || true)
    total=$(grep -c -E '^\s*- \[[ x]\]' "$c/plan.md" || true)
  fi
  reviewed=no; [[ -f "$c/review.md" ]] && reviewed=yes
  case "${status:-none}" in
    exploring) next="propose" ;;
    proposed)  next="grill | iterate (optional) → apply" ;;
    applying)  next="apply" ;;
    applied)   [[ $reviewed == yes ]] && next="archive" || next="adversarial-code-review" ;;
    *)         next="propose (no frontmatter)" ;;
  esac
  echo "$name · ${status:-?} · $done_n/$total · reviewed=$reviewed · next: $next"
done
[[ $found == 1 ]] || echo "no changes"
