#!/usr/bin/env bash
# Check a Local Gateway over Tailscale: node visible? /health ok?
# Usage: gateway-check.sh <tailnet-ip:port>
# Exits 0 on success, 1 with a message on failure.
set -euo pipefail

TARGET="${1:?usage: gateway-check.sh <tailnet-ip:port>}"

if ! tailscale status >/dev/null 2>&1; then
  echo "NOT_ENROLLED: run 'tailscale up' and approve the link first" >&2
  exit 1
fi

PROXY="${HTTPS_PROXY%:*}:3130"
RESP=$(curl --proxy "$PROXY" --fail-with-body -sS -m 30 "http://$TARGET/health" 2>&1) || {
  echo "HEALTH_FAILED: $RESP" >&2
  exit 1
}
echo "$RESP" | grep -q '"ok"[[:space:]]*:[[:space:]]*true' || {
  echo "HEALTH_NOT_OK: $RESP" >&2
  exit 1
}
echo "OK: $TARGET healthy"
