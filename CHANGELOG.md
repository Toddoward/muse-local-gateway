# Changelog

## Unreleased

- Skill name is now `muse-local-gateway` (lowercase-hyphen, the Agent Skills convention).

## 0.1.0 — 2026-10-12

First public release.

- **gateway** (`:8730`): `PUT /files/<path>` into one shared folder, tailnet-only, path-escape safe.
- **bench** (`:8731`): `POST /exec` in a container with no secrets, no Docker socket, not privileged.
- **Network modes** chosen at setup: `isolated` (default; internet via a proxy that refuses host,
  LAN and tailnet), `lan-allow` (plus listed LAN devices over HTTP), `open` (with a warning).
- **USB serial** (`compose.usb.yaml`): serial devices only, hot-plug safe. Windows via usbipd-win
  with a watcher that keeps drivers loaded across WSL restarts.
- **Setup** for Linux/macOS (`setup.sh`) and Windows (`setup.ps1`), tailnet ACL example,
  experimental direct module, smoke test (`tests/smoke.py`).
- The bench image includes `libusb-1.0-0`, so USB toolchains (ESP-IDF's openocd) install cleanly.
- Logo `>_` (shared with muse-gadget-forge): one continuous ribbon, split where it passes behind itself, drawn as a
  gradient spline in Muse blues (`docs/media/make_logo.py`; master in Figma).
- README hero: a 15 s animated SVG in Muse's palette, light/dark and English/Korean (`docs/media/make_hero.py`).
- Docs in English and Korean.
