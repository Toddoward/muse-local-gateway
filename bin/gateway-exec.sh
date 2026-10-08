#!/usr/bin/env bash
# Run a command on a gateway bench container over Tailscale, wait for it.
# Usage: gateway-exec.sh <tailnet-ip:port> <cmd> [cwd] [timeout]
# Prints remote stdout, then stderr (labeled). Exits with the remote exit code.
# Long jobs: POST waits up to 50s (wait), then polls GET /exec/<id> every 10s.
set -euo pipefail

TARGET="${1:?usage: gateway-exec.sh <tailnet-ip:port> <cmd> [cwd] [timeout]}"
CMD="${2:?cmd required}"
CWD="${3:-/work}"
TIMEOUT="${4:-600}"

PROXY="${HTTPS_PROXY%:*}:3130"
BASE="http://$TARGET"

payload=$(python3 -c 'import json,sys; print(json.dumps({"cmd": sys.argv[1], "cwd": sys.argv[2], "timeout": int(sys.argv[3]), "wait": 50}))' "$CMD" "$CWD" "$TIMEOUT")
resp=$(curl --proxy "$PROXY" --fail-with-body -sS -m 90 \
  -X POST -H 'Content-Type: application/json' -d "$payload" "$BASE/exec")

get() { python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("'"$1"'",""))' <<<"$resp"; }

id="$(get id)"; status="$(get status)"
while [ "$status" = "running" ]; do
  sleep 10
  resp=$(curl --proxy "$PROXY" --fail-with-body -sS -m 60 "$BASE/exec/$id")
  status="$(get status)"
done

python3 -c '
import json,sys
d = json.load(sys.stdin)
sys.stdout.write(d.get("stdout") or "")
if d.get("stderr"): sys.stderr.write("--- stderr ---\n" + d["stderr"])
sys.stderr.write("[status=%s exit=%s truncated=%s elapsed=%s]\n" % (d.get("status"), d.get("exit_code"), d.get("truncated"), d.get("elapsed")))
sys.exit(d.get("exit_code") if isinstance(d.get("exit_code"), int) else 1)
' <<<"$resp"
