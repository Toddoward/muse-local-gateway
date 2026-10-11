[![English](https://img.shields.io/badge/lang-English-111111?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey?style=flat-square)](README.kr.md)

# Muse Gadgets SDK — how it fits

The official SDKs (`facebookincubator/muse-gadget-sdk`, Apache 2.0) and
this skill solve neighboring problems. Read this before wiring them
together.

## The two SDKs

**Linux Device SDK** — the official "hands on the machine":
- Install: `bash install.sh --sdk-token mgst_…` on the machine itself.
- Muse gets: `system.run`, `file.read`, `file.write` (64 KB chunks),
  `device.health` — as the installing account (sudo included, if it has it).
- Pairing: Bluetooth LE + Muse app (Developer mode) + SDK token.
- Linux-only (Pi OS / Debian / Ubuntu), app-side.

**ESP32 Device SDK** — the device is independent at runtime:
- Flash via USB serial (ESP-IDF v6.0.1), pair via the app, then it lives
  on home Wi-Fi with a tunnel back to Muse.
- **It does not route through the local machine at runtime.** USB is for
  flashing and logs only.

## The honest architecture

```
Local Gateway (this skill)          Muse Gadgets SDK (official)
─────────────────────────           ────────────────────────────
agent-side (the Muse agent, me)     app-side (Muse app + phone)
cross-platform (Win/Linux/Mac)      Linux-only (Linux SDK) / any (ESP32)
Tailscale, no Bluetooth needed       Bluetooth LE + SDK token + app pairing
```

They complement; neither replaces the other. On Windows/macOS, the Local
Gateway is the only agent-side path.

## The ESP32 dev-station pattern (recommended)

1. Enable `extensions/usb-serial/` so the container sees the board.
2. Muse (via the gateway) builds and flashes: `idf.py build`,
   `idf.py -p /dev/ttyUSB0 flash`, `idf.py monitor`.
3. The board pairs with the Muse app once; from then on it talks to Muse
   over Wi-Fi by itself.

The container is the **dev station**, not a runtime proxy. Do not design
flows that need the container to relay the ESP32's traffic.

## Custom commands

- Linux gadget: add to `COMMAND_SPECS` in `src/musegadget/executor.py`.
- ESP32: advertise in `link.register`, handle in `main/app.c`.
- The repo's `AGENTS.md` files are written for coding agents.

## Terms to respect

Every gadget needs an SDK token from `gadgets.muse.ai`; read the Gadget
SDK Terms before flashing or pairing. Tokens are identifiers, not
passwords — if one leaks, revoke and rebuild.
