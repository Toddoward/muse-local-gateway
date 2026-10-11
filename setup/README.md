[![English](https://img.shields.io/badge/lang-English-111111?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey?style=flat-square)](README.kr.md)

# Setup — pick your OS

One-command setup per OS. All three install the **container** module
(recommended); the direct module is a manual follow-up (see
`../modules/direct/`).

## Capability matrix (honest)

| | Linux | Windows | macOS |
|---|---|---|---|
| Container gateway | ✅ | ✅ (Docker Desktop) | ✅ (Docker Desktop) |
| Tailscale | ✅ | ✅ | ✅ |
| USB-serial passthrough | ✅ (`--device`) | ⚠️ needs usbipd-win | ❌ (Docker Desktop can't) |
| Bluetooth from container | ⚠️ (`--net=host`, privileged) | ❌ | ❌ |
| LAN devices from container | ✅ (`--net=host`) | ⚠️ limited | ⚠️ limited |

Details: `../extensions/`.

## Run it

**Linux:**
```bash
bash setup/linux/setup.sh
```

**Windows (PowerShell, admin):**
```powershell
.\setup\windows\setup.ps1
```

**macOS:**
```bash
bash setup/mac/setup.sh
```

Each script checks prerequisites, then brings up `modules/container/`.
After that, share the tailnet IP:port with Muse and verify together.
