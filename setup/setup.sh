#!/usr/bin/env bash
# Muse Local Gateway setup for Linux and macOS.
# Picks the network mode, writes .env (chmod 600), starts the stack, prints what to tell Muse.
# Re-run any time: an existing .env is kept (delete it to choose again).
set -euo pipefail
cd "$(dirname "$0")/.."

die() { echo "ERROR: $*" >&2; exit 1; }
command -v docker >/dev/null || die "Docker is required: https://docs.docker.com/get-docker/"
docker compose version >/dev/null 2>&1 || die "Docker Compose v2 is required (docker compose ...)"

if [ -f .env ]; then
  echo "Keeping existing .env (delete it to choose the mode again)."
else
  cat <<'TXT'
How far may Muse's shell (the bench) reach?
  1) isolated  - internet through a proxy only; your computer and LAN are blocked  (recommended)
  2) lan-allow - isolated, plus specific LAN devices you list (HTTP APIs: Shelly, Tasmota, ...)
  3) open      - your computer and the whole LAN, every protocol
TXT
  read -rp "Choose [1]: " mode
  files="compose.yaml"; lan=""
  case "${mode:-1}" in
    1) ;;
    2) read -rp "LAN device IPs, space-separated: " lan
       for ip in $lan; do [[ $ip =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}(/[0-9]{1,2})?$ ]] || die "not an IPv4 address: $ip"; done ;;
    3) cat <<'TXT'
WARNING: in "open" mode, if Muse is ever tricked by a malicious web page or file (prompt injection),
the shell it controls can reach your router admin page, NAS, and every service on this computer.
TXT
       read -rp 'Type "open" to confirm: ' ok; [ "$ok" = open ] || die "cancelled"
       files="$files;compose.open.yaml" ;;
    *) die "choose 1, 2 or 3" ;;
  esac
  if [ "$(uname)" = Linux ]; then
    read -rp "Let the bench use USB serial boards (ESP32 etc.)? [y/N] " usb
    [ "${usb:-n}" = y ] && files="$files;compose.usb.yaml"
  else
    echo "(macOS: Docker Desktop cannot pass USB devices to containers; USB serial is skipped.)"
  fi
  echo "Tailscale auth key: admin console -> Settings -> Keys -> Generate auth key,"
  echo "  Reusable off, Tags: tag:muse-gw  (add the policy in examples/tailnet-acl.hujson first)."
  read -rsp "Paste the key (input hidden): " key; echo
  [ -n "$key" ] || die "an auth key is required"
  umask 077
  cat > .env <<ENV
TS_AUTHKEY=$key
TS_HOSTNAME=muse-gateway
MUSE_SHARE=./shared
LAN_ALLOW=$lan
MAX_UPLOAD_MB=200
COMPOSE_FILE=$files
COMPOSE_PATH_SEPARATOR=;
ENV
  echo "Wrote .env (mode: ${files//;/ + })"
fi

mkdir -p shared tailscale-state
docker compose up -d --build

echo "Waiting for the tailnet address..."
ip=""
for _ in $(seq 60); do
  ip=$(docker compose exec -T tailscale tailscale ip -4 2>/dev/null | head -1 || true)
  [ -n "$ip" ] && break; sleep 2
done
[ -n "$ip" ] || die "no tailnet address yet. Check: docker compose logs tailscale"

cat <<TXT

Done. Send this to Muse:
----------------------------------------------------------------------
Install the muse-local-gateway skill from
https://github.com/Toddoward/muse-local-gateway (SKILL.md).
My gateway: files http://$ip:8730, shell http://$ip:8731
Run bin/gateway-check.sh $ip:8730 first.
----------------------------------------------------------------------
Then in the Tailscale admin console, tag the Muse device tag:muse.
Shared folder: $(pwd)/shared
TXT
