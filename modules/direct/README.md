[![English](https://img.shields.io/badge/lang-English-111111?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey?style=flat-square)](README.kr.md)

# Direct module (host install)

For users who want Muse across the machine, not sandboxed in a
container. The gateway runs on the host itself and serves the same API
(see `../container/gateway-spec.md`).

## When to pick this
- You want Muse to reach your files, tools, and scripts directly.
- You accept that Muse sees what the gateway's user account sees.

## When NOT to pick this
- The machine holds anything you wouldn't hand to Muse. Use the
  container module instead.

## Setup
1. Install Tailscale on the host and join the tailnet.
2. Run a gateway implementing `gateway-spec.md` on the host
   (reference port `8730`), bound to the tailnet interface.
3. Set the tailnet ACL to pin Muse's node to the gateway port only.
4. Share the tailnet IP:port with Muse; verify with `bin/gateway-check.sh`.

## Security notes
- Run the gateway as a dedicated low-privilege user when possible.
- The gateway's file root should still be a designated folder — "direct"
  does not mean "the whole disk" unless the user means it.
- Everything in the top-level SKILL.md Security notes applies.
