[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](README.kr.md)

# 확장 — 게이트웨이에서 장치에 닿기

게이트웨이를 연결한 뒤, 이 확장들을 켜면 Muse가 내 컴퓨터에 연결된 하드웨어를 다룰 수 있습니다.

| 확장 | 내용 | Linux | Windows | macOS |
|---|---|---|---|---|
| [`usb-serial/`](usb-serial/README.kr.md) | ESP32·시리얼 장치 (펌웨어 굽기, 로그 보기) | ✅ | ⚠️ usbipd-win 필요 | ❌ |
| [`bluetooth/`](bluetooth/README.kr.md) | BT/BLE 장치 | ⚠️ 제한적 | ❌ | ❌ |
| [`lan/`](lan/README.kr.md) | LAN의 HTTP 장치, Home Link | ✅ | ⚠️ | ⚠️ |

원칙은 하나입니다. 컨테이너는 OS가 열어 주는 것만 만질 수 있습니다.
Linux가 가장 많이 열어 주고, Docker Desktop(Windows/macOS)은 막혀 있는 부분이 많습니다.
