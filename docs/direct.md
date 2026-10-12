[![English](https://img.shields.io/badge/lang-English-111111?style=flat-square)](direct.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey?style=flat-square)](direct.kr.md)

# Direct module (experimental)

The same gateway and shell, running on the host itself instead of in containers. Linux and macOS.

**Muse gets the rights of the user account that runs it** — every file, tool, and network that account
can reach. No container, no network modes, no proxy, no audit of web requests. Read
[SECURITY.md](../SECURITY.md) first. Prefer the container setup unless you have a reason.

Good reasons: a dedicated machine (a Raspberry Pi on your desk) that exists for Muse to work on,
under its own low-privilege account.

## Run

Needs `python3` and Tailscale on the host, logged in, with this machine tagged `tag:muse-gw`
(see [`examples/tailnet-acl.hujson`](../examples/tailnet-acl.hujson)).

```bash
MUSE_SHARE=~/muse-share ./direct/run.sh     # Ctrl+C stops both and removes the serve entries
```

Both servers listen on `127.0.0.1` only; `tailscale serve` forwards tailnet `:8730` and `:8731`
to them. Any program on this machine can call them too — that is the point of "direct".
