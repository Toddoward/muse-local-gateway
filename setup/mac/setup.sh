#!/usr/bin/env bash
# Local Gateway one-command setup for macOS.
# Installs the container module (recommended).
# NOTE: Docker Desktop on macOS cannot pass USB devices through to
# containers — the usb-serial extension is not available here. The file
# gateway itself works fine.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR/modules/container"

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1 — $2"; exit 1; }; }

need docker "install Docker Desktop: https://www.docker.com/products/docker-desktop/"
need tailscale "install Tailscale: https://tailscale.com/download/mac"

mkdir -p shared tailscale-state

echo "==> starting gateway + tailscale sidecar"
docker compose up -d

echo
echo "Next steps:"
echo "  1. Join the tailnet if prompted."
echo "  2. Find the tailnet IP and share <tailnet-ip>:8730 with Muse."
echo "  3. Limitation: USB device passthrough is NOT available under Docker"
echo "     Desktop on macOS. Use a Linux box for the usb-serial extension"
echo "     (see ../../extensions/usb-serial/)."
