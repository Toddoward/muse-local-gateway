[![English](https://img.shields.io/badge/lang-English-111111?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey?style=flat-square)](README.kr.md)

# Muse Local Gateway

A gateway that lets Muse AI reach your own machine — a home PC, a lab box, or a home server — directly.

Files, commands, and local data travel over Tailscale with no relay server. No port forwarding, no public exposure. You decide how much of your machine Muse can see.

> **Status:** modular draft (2026-10-08). The K12 deployment is verified live.
> The distributable modules are newly written and awaiting field testing.

## Why

- Muse runs in a cloud VM. To reach the files, USB devices, or local models on your PC, it needs a way in.
- This gateway is that way in. Run a small server on your machine, and Muse uploads files and collects results directly over your tailnet.

## Choose a module

| | Container (recommended) | Direct |
|---|---|---|
| How | Docker + Tailscale sidecar | Installed on the host |
| What Muse sees | Only the folders you bind-mount | The whole computer (your choice) |
| Isolation | Sandboxed | None |
| Start | [`modules/container/`](modules/container/README.md) | [`modules/direct/`](modules/direct/README.md) |

Per-OS setup: [`setup/`](setup/README.md) (Windows / Linux / macOS)

## What's inside

- **[`modules/container/`](modules/container/README.md)** — the recommended way. Docker Compose for the gateway container and its Tailscale sidecar, plus the gateway API spec
- **[`modules/direct/`](modules/direct/README.md)** — install on the host, for when you want to hand Muse the whole machine
- **[`setup/`](setup/README.md)** — one-command setup per OS, with a capability matrix (USB passthrough and more differ by OS)
- **[`extensions/`](extensions/README.md)** — after connecting: USB serial, Bluetooth, and LAN device access
- **[`gadgets/`](gadgets/README.md)** — how this fits with the Muse Gadgets SDK (what works and what doesn't)
- **`bin/`** — Muse-side tools: `gateway-check.sh`, `gateway-put.sh`, `gateway-exec.sh`

## Gateway API (summary)

| Item | Value |
|---|---|
| Upload a file | `PUT /files/<relative-path>` |
| Health check | `GET /health` → `{"ok": true}` |
| Auth | None on the tailnet. The tailnet ACL pins Muse's node to the gateway port |

Full spec: [`modules/container/gateway-spec.md`](modules/container/gateway-spec.md)

## Security principles

- Commands run in a **separate, secrets-free container**, apart from the file gateway
- The tailnet ACL pins Muse's node to each container's port only
- Path traversal (`..`, absolute paths) is rejected
- The network isolation mode is chosen at install (default and recommended: `isolated`)

## For AI agents

How Muse uses this skill: [SKILL.md](SKILL.md)
