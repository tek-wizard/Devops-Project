#!/usr/bin/env bash
# Generate steady traffic against the backend so the HPA and the Grafana
# dashboard have something to show. Ctrl-C to stop.
# Usage: scripts/load-test.sh [base_url]   (default: http://localhost:8100)
set -euo pipefail

BASE="${1:-http://localhost:8100}"
echo "Sending traffic to $BASE (Ctrl-C to stop)..."

i=0
while true; do
  i=$((i + 1))
  curl -s -o /dev/null "$BASE/api/tickets"
  curl -s -o /dev/null "$BASE/api/tickets/stats/summary"
  curl -s -o /dev/null "$BASE/health"
  if [ $((i % 7)) -eq 0 ]; then
    curl -s -o /dev/null -X POST "$BASE/api/tickets" \
      -H 'Content-Type: application/json' \
      -d "{\"title\":\"load ticket $i\",\"priority\":\"medium\"}"
  fi
  sleep 0.2
done
