---
name: "muse_local_gateway"
description: "Give Muse direct access to the user's own local machine over Tailscale: place files, read back results, and work with local data. Use when the user wants Muse to reach their home PC, lab box, or home server directly instead of through a relay."
---

# Muse Local Gateway

> Status: modular draft (2026-10-08). The K12 deployment is verified live;
> the distributable modules below are new and await field testing.

## The idea
The user runs a small gateway on their own machine. Muse reaches it over
Tailscale and exchanges files directly — no relay, no port forwarding, no
public exposure. The user decides how much of their machine Muse may see.

## Choose your module

| | Container (recommended) | Direct host |
|---|---|---|
| What | Gateway in Docker + Tailscale sidecar | Gateway on the machine itself |
| Muse sees | Only bind-mounted folders | Across the computer |
| Isolation | Sandboxed | None — your choice |
| Start | `modules/container/` | `modules/direct/` |

Then pick your OS setup: `setup/` (Windows / Linux / macOS).

## Module index

- **`modules/container/`** — the recommended way. Docker Compose with the
  gateway container and Tailscale sidecar, plus the gateway API spec.
- **`modules/direct/`** — the gateway on the host itself, for users who
  want Muse across the machine.
- **`setup/`** — one-command setup per OS, with an honest capability
  matrix (USB passthrough etc. differ by OS).
- **`extensions/`** — after connecting: reach USB-serial, Bluetooth, and
  LAN devices from the gateway.
- **`gadgets/`** — how the Muse Gadgets SDK fits (and where it doesn't).
- **`bin/`** — Muse-side tools: `gateway-check.sh`, `gateway-put.sh`, `gateway-exec.sh` (POST /exec + poll until done).

## The contract (gateway API)
| Item | Value |
|---|---|
| Upload | `PUT /files/<relative-path>` — body is the file content |
| Health | `GET /health` → `{"ok": true}` |
| Auth | None on the tailnet. The gateway trusts tailnet identity: the tailnet ACL pins Muse's node to the gateway port, and Tailscale cryptographically authenticates every peer |
| Paths | Only under the owner-designated folder(s). `..`, absolute paths, backslashes → `400` |
| Headers | `Content-Length` required (missing → `411`). Enforce a max size (reference: 200MB → `413`) |
| Success | `201 {"path": "<relative-path>", "bytes": <size>}` |
| Same name | Overwrites. Date-stamp filenames to preserve |

Full spec: `modules/container/gateway-spec.md`. Do NOT hardcode folder
names like `drop`/`work` — those were one deployment's convention.

## Muse-side procedure
1. `tailscale status` — is the user's gateway node listed and enrolled?
   If not, run `tailscale up`, show the approval link, and wait.
2. `GET /health` on the gateway's tailnet address — expect `{"ok": true}`.
3. Only then `PUT /files/<path>`.
4. Report: what was placed and where. List each file when several.
5. On failure: do NOT retry in a loop. Tell the user, distinguishing
   node-not-visible / health-failed / upload-rejected.

## Tooling
Runtime shim, NOT the upstream CLI: `/opt/hatch/bin/tailscale`
(`up`, `down`, `status`, `ip` only). No `--authkey` — approval-link join
is the only path.

The tailnet is NOT reachable by ordinary networking. Reuse the runtime
proxy with port 3130 (see `bin/gateway-check.sh`, `bin/gateway-put.sh`).
TCP only — never ping/ICMP/UDP. This VM is outbound-only: it can only
initiate connections, never accept them.

## Security notes
- Tailnet ACL should pin Muse's node to the gateway port only.
- The gateway must reject path traversal (`..`, absolute paths).
- Never handle keys in plaintext; this design needs none.
- Do not expose tailnet IPs or machine names beyond the task at hand.
- Tailscale support here is experimental: after a VM replacement,
  re-verify with `tailscale status`.
- Command execution belongs in a **separate, secrets-free container**
  (K12 reference: `muse-bench`), never in the file gateway. The tailnet
  ACL then pins Muse's node to each container's port only.

## Network isolation modes (install-time choice)

When the gateway includes command execution (a bench/worker container),
the owner picks one network mode at install. **`isolated` is the
recommended default** — the same posture as keeping exec in a separate
secrets-free container.

| Mode | What it allows | How |
|---|---|---|
| **`isolated`** (recommended, default) | Internet only, via proxy. Host and LAN blocked | bench on an `internal` network only; the egress proxy refuses private destinations (`egress.conf`) |
| `lan-allow` | Above + **owner-specified LAN devices only** (HTTP-API IoT: Shelly, Tasmota, ESPHome web, …) | `acl lan_allow dst <IP>` + `http_access allow lan_allow` **before** `deny private` in `egress.conf` |
| `open` | Host + LAN fully, all protocols (MQTT, CoAP, UDP, mDNS discovery) | bench on a normal network, proxy env vars removed |

- `lan-allow` only passes clients that speak HTTP(S)/CONNECT. MQTT, UDP,
  or device discovery (mDNS) need `open`.
- Choosing `open` must come with an **explicit warning**: if Muse is ever
  prompt-injected, that shell reaches the owner's whole home network
  (router admin, NAS, host-local services). On Docker Desktop, host
  `127.0.0.1`-only services are reachable via `host.docker.internal`.
- In every mode: **no secrets in the exec container**, no `docker.sock`
  mount, no `privileged`.
