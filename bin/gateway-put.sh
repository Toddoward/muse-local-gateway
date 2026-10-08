#!/usr/bin/env bash
# Upload a file to a Local Gateway over Tailscale.
# Usage: gateway-put.sh <tailnet-ip:port> <local-file> <remote-path>
# Prints the gateway's 201 JSON on success.
set -euo pipefail

TARGET="${1:?usage: gateway-put.sh <tailnet-ip:port> <local-file> <remote-path>}"
SRC="${2:?local file required}"
DEST="${3:?remote path required}"
[ -f "$SRC" ] || { echo "NO_SUCH_FILE: $SRC" >&2; exit 1; }

PROXY="${HTTPS_PROXY%:*}:3130"
curl --proxy "$PROXY" --fail-with-body -sS -m 120 \
  -X PUT --data-binary "@$SRC" \
  "http://$TARGET/files/$DEST"
echo
