#!/usr/bin/env bash
# Direct module (experimental): gateway + bench on the host itself, Linux/macOS.
# Muse gets the rights of THIS user account — files, tools, network, everything it can reach.
# No container, no network modes, no proxy. Read SECURITY.md before using it.
#
#   MUSE_SHARE=~/muse-share ./direct/run.sh        # Ctrl+C stops both
#
# Needs python3 and Tailscale on the host, logged in, with this machine tagged tag:muse-gw.
set -euo pipefail
cd "$(dirname "$0")/.."
share="${MUSE_SHARE:-$HOME/muse-share}"
mkdir -p "$share"

# Both listen on loopback only; `tailscale serve` forwards tailnet :8730/:8731 from 127.0.0.1.
export BIND=127.0.0.1 TAILNET_PEER_HOST=127.0.0.1
SHARE_DIR="$share" python3 gateway/gateway.py &
WORK_DIR="$share" python3 bench/bench.py &
trap 'kill $(jobs -p) 2>/dev/null; tailscale serve --tcp 8730 off; tailscale serve --tcp 8731 off' EXIT
tailscale serve --bg --tcp 8730 tcp://127.0.0.1:8730
tailscale serve --bg --tcp 8731 tcp://127.0.0.1:8731
echo "Serving $share on $(tailscale ip -4 | head -1):8730 (files) and :8731 (shell). Ctrl+C to stop."
wait
