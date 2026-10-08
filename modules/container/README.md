# Container module (recommended)

The gateway runs in Docker, next to a Tailscale sidecar. Muse only ever
sees inside the container — bind mounts decide what that is.

## Layout

```yaml
# docker-compose.yml (this folder)
services:
  gateway:    # the file API; implements gateway-spec.md
  tailscale:  # sidecar joining the tailnet; the HOST stays off the tailnet
```

## Quick start

```bash
cd modules/container
docker compose up -d
# join the tailnet when prompted, then share the tailnet IP:port with Muse
```

## What to mount

Mount the folders you want Muse to use, e.g.:

```yaml
volumes:
  - ./shared:/data     # the ONE folder Muse may use
```

Change the host path freely. Do not hardcode `drop`/`work`.

## Approvals (two taps)

1. Muse's `tailscale up` prints a link — open it to admit the `muse`
   device to the tailnet.
2. Muse's first connection to the gateway address needs one approval.
   (Later connections to the same address are covered.)

Also allow the protocol in the Muse app:
Settings > Permissions > Direct network protocols.

## See also

- `gateway-spec.md` — the API the gateway image must implement.
- `../../extensions/` — USB/Bluetooth/LAN from the container.
- `../../setup/` — OS-specific one-command setup.
