#!/usr/bin/env bash
# Local Gateway one-command setup for Linux.
# Installs the container module (recommended). Run with a user in the docker group.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR/modules/container"

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1 — $2"; exit 1; }; }

need docker "install Docker Engine: https://docs.docker.com/engine/install/"
need tailscale "install Tailscale: https://tailscale.com/download/linux"

mkdir -p shared tailscale-state

echo "==> starting gateway + tailscale sidecar"
docker compose up -d

echo
echo "Next steps:"
echo "  1. Join the tailnet if prompted (tailscale up on this machine is already done via the sidecar auth flow)."
echo "  2. Find the tailnet IP:  tailscale ip -4  (inside the sidecar: docker exec <tailscale-ctr> tailscale ip -4)"
echo "  3. Share <tailnet-ip>:8730 with Muse and verify together."
echo "  4. USB devices: add '--device=/dev/ttyUSB0' style entries to docker-compose.yml (see ../../extensions/usb-serial/)."
