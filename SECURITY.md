[![English](https://img.shields.io/badge/lang-English-111111?style=flat-square)](SECURITY.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey?style=flat-square)](SECURITY.kr.md)

# Security

## Reporting a vulnerability

Use GitHub's private reporting: **Security → Report a vulnerability** on this repository.
Please don't open a public issue for anything that lets someone get past the locks below.

## What this stack is defending against

The realistic threat is not someone breaking into Tailscale. It is **Muse being tricked**:
a web page, a file, or a message carrying instructions (prompt injection) that make Muse run
commands you never asked for. Everything below assumes that can happen.

## What an attacker controlling Muse could do

| | `isolated` (default) | `lan-allow` | `open` | direct module |
|---|---|---|---|---|
| Read, change, delete files in the shared folder | yes | yes | yes | yes |
| **Send shared-folder files to the internet** | **yes** (via the proxy) | yes | yes | yes |
| Use your CPU, disk space, bandwidth | yes | yes | yes | yes |
| Reflash boards on USB (if you enabled USB) | yes | yes | yes | yes |
| Reach the LAN devices you listed | no | **yes**, HTTP(S) | yes | yes |
| Reach your router, NAS, other LAN devices | no | no | **yes** | yes |
| Reach services on this computer (even `127.0.0.1`-only ones¹) | no | no | **yes** | yes |
| Read files outside the shared folder | no | no | no | **yes** |
| Read secrets: your Tailscale key, browser data, SSH keys | no | no | no | **yes** |
| Reach other machines on your tailnet | no | no | **yes, if this computer itself runs Tailscale**² | yes |
| Control Docker / escape to the host | no³ | no³ | no³ | n/a |

¹ Docker Desktop forwards `host.docker.internal` to the host's loopback services.
² The sidecar is the gateway's only tailnet node and the bench cannot route through it. But in `open` mode the
bench uses this computer's own network — if Tailscale is also installed on the host, its routes come with it.
³ No Docker socket, not privileged, only serial devices allowed. A container escape would need a
kernel or Docker vulnerability — keep both updated.

## So, in practice

- **Treat the shared folder as readable by the internet.** Never put secrets, keys, or personal
  documents there. Copy in what Muse needs, copy out what it made.
- **Stay on `isolated` unless you need more.** `lan-allow` is fine for a few HTTP devices.
  Choose `open` only for protocols the proxy can't carry (MQTT, UDP, mDNS), and know what it opens.
- **Tag the Muse device `tag:muse`.** An untagged Muse device counts as one of *your* devices and
  the default policy gives it everything on your tailnet. This is the single most important step.
- **Use a one-off, tagged auth key** (`tag:muse-gw`, reusable off). `.env` and `tailscale-state/`
  hold credentials: never commit or share them (`.gitignore` already excludes them).
- **Cut off in one step:** remove Muse's device in the Tailscale admin console, or `docker compose down`.

## Where to look

```bash
docker compose logs bench                                   # every command Muse ran (not its output)
docker compose logs gateway                                 # every upload (path + status, not contents)
docker compose exec egress tail /var/log/squid/access.log   # every web request the shell made
```

## What this does not protect

- Muse's own platform or your Muse account being compromised.
- Your Tailscale account being compromised (an admin can change the ACL).
- Anything you place in the shared folder (see above).
