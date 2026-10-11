[![English](https://img.shields.io/badge/lang-English-111111?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey?style=flat-square)](README.kr.md)

# Bluetooth extension

## Honest status: limited

Bluetooth from inside a container is only practical on Linux, and even
there it needs `--net=host` plus privileges — which weakens the
sandboxing the container module is for. On Docker Desktop (Windows/macOS)
it is effectively unavailable.

## Linux (best effort)

```yaml
services:
  gateway:
    network_mode: host
    privileged: true
    volumes:
      - /var/run/dbus:/var/run/dbus
```

Understand what you give up: `privileged` + host networking removes most
container isolation. Prefer the direct module on a dedicated box if you
need this.

## Recommendation

For Bluetooth gadgets, use the **Muse Gadgets SDK pairing flow**
instead: the gadget pairs over Bluetooth LE with the Muse app on the
phone (see `../../gadgets/`). The container does not need to speak
Bluetooth at all.
