[![English](https://img.shields.io/badge/lang-English-111111?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey?style=flat-square)](README.kr.md)

# Extensions — reach devices from the gateway

After the gateway is connected, these extensions let Muse work with
hardware attached to the local machine.

| Extension | What | Linux | Windows | macOS |
|---|---|---|---|---|
| `usb-serial/` | ESP32 / serial devices (flash, monitor) | ✅ | ⚠️ via usbipd-win | ❌ |
| `bluetooth/` | BT/BLE devices | ⚠️ limited | ❌ | ❌ |
| `lan/` | LAN HTTP devices, Home Link | ✅ | ⚠️ | ⚠️ |

The honest rule: the container can only touch what the OS lets through.
Linux gives the most; Docker Desktop (Win/Mac) is fenced in.
