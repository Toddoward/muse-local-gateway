# LAN extension

Reach devices on the home network from the gateway: TVs, speakers,
printers, anything with a local HTTP API — and Muse Home Link.

## Linux

`--net=host` puts the container on the LAN directly:

```yaml
services:
  gateway:
    network_mode: host
```

## Windows / macOS (Docker Desktop)

Host networking is not available. The container sees the LAN through the
Desktop VM's NAT — most discovery protocols (mDNS, SSDP) break. Options:

- Run the gateway via the **direct module** on the host instead.
- Or put a **Muse Home Link** (or any ESP32 gadget with the home-network
  tunnel) on the LAN and let Muse reach devices through it.

## Muse Home Link

Meta's own gadget: a USB-C device on home Wi-Fi that lets Muse talk to
TVs, speakers, lights, printers, and anything exposing HTTPS or a local
HTTP API. Community skills cover Philips Hue, Sonos, Apple TV, Google
Nest, Samsung TVs. The Home Link code is open source (see `../../gadgets/`).
