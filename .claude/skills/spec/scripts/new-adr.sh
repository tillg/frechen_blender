#!/usr/bin/env bash
# Create a new ADR from specs/templates/adr.md with the next free number and a 4-letter hash.
# Usage: new-adr.sh <slug> [<title>]   — prints the new file path and id. Run from the repo root.
set -euo pipefail
slug="${1:?usage: new-adr.sh <slug> [<title>]}"
title="${2:-$slug}"
dir="specs/architecture"
tpl="specs/templates/adr.md"
[[ -f "$tpl" ]] || { echo "missing $tpl" >&2; exit 1; }
mkdir -p "$dir/archive"
last=$(ls "$dir" "$dir/archive" 2>/dev/null | sed -n 's/^adr-\([0-9]\{3\}\)-.*/\1/p' | sort -n | tail -1)
num=$(printf '%03d' $(( 10#${last:-0} + 1 )))
# bounded read first: an unbounded `tr </dev/urandom | head` dies of SIGPIPE under pipefail
hash=$(head -c 1024 /dev/urandom | LC_ALL=C tr -dc 'a-z' | head -c 4)
[[ ${#hash} == 4 ]] || hash=$(printf '%04d' $RANDOM | tr '0-9' 'a-j')
id="ADR-${num}-$(echo "$hash" | tr a-z A-Z)"
file="$dir/adr-${num}-${hash}-${slug}.md"
today=$(date +%F)
sed -e "s/ADR-NNN-HHHH/${id}/g" -e "s/<Title>/${title}/g" -e "s/YYYY-MM-DD/${today}/g" "$tpl" >"$file"
echo "$id $file"
