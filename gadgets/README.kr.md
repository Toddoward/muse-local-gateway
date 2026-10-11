[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](README.kr.md)

# Muse Gadgets SDK — 어떻게 맞물리나

공식 SDK(`facebookincubator/muse-gadget-sdk`, Apache 2.0)와 이 스킬은 서로 이웃한 문제를 풉니다. 둘을 엮기 전에 읽어 주세요.

## 두 SDK

**Linux Device SDK** — 공식 "컴퓨터 위의 손":
- 설치: 그 컴퓨터에서 `bash install.sh --sdk-token mgst_…`
- Muse가 얻는 것: `system.run`, `file.read`, `file.write`(64 KB 단위), `device.health` — 설치한 계정 권한으로 동작합니다(그 계정에 sudo가 있으면 sudo까지).
- 페어링: Bluetooth LE + Muse 앱(개발자 모드) + SDK 토큰
- Linux 전용(Pi OS / Debian / Ubuntu), 앱 쪽에서 동작

**ESP32 Device SDK** — 동작 중에는 장치가 혼자 섭니다:
- USB 시리얼로 굽고(ESP-IDF v6.0.1), 앱으로 페어링하면, 이후 집 Wi-Fi에서 Muse로 터널을 열고 지냅니다.
- **동작 중에는 로컬 컴퓨터를 거치지 않습니다.** USB는 굽기와 로그 보기에만 씁니다.

## 실제 구조

```
Local Gateway (이 스킬)              Muse Gadgets SDK (공식)
─────────────────────────           ────────────────────────────
에이전트 쪽 (Muse 에이전트)            앱 쪽 (Muse 앱 + 휴대폰)
여러 OS (Win/Linux/Mac)              Linux 전용 (Linux SDK) / 무관 (ESP32)
Tailscale, 블루투스 불필요             Bluetooth LE + SDK 토큰 + 앱 페어링
```

둘은 서로 보완하며, 어느 쪽도 다른 쪽을 대신하지 않습니다. Windows/macOS에서는 Local Gateway가 유일한 에이전트 쪽 경로입니다.

## ESP32 개발 스테이션 방식 (권장)

1. [`extensions/usb-serial/`](../extensions/usb-serial/README.kr.md)을 켜서 컨테이너가 보드를 보게 합니다.
2. Muse가 게이트웨이를 통해 빌드하고 굽습니다: `idf.py build`, `idf.py -p /dev/ttyUSB0 flash`, `idf.py monitor`
3. 보드는 Muse 앱과 한 번 페어링하고, 그 뒤로는 Wi-Fi로 Muse와 직접 대화합니다.

컨테이너는 **개발 스테이션**이지 동작 중 중계기가 아닙니다. 컨테이너가 ESP32의 통신을 중계해야 하는 흐름은 설계하지 마세요.

## 사용자 정의 명령

- Linux 가젯: `src/musegadget/executor.py`의 `COMMAND_SPECS`에 추가
- ESP32: `link.register`에 알리고 `main/app.c`에서 처리
- SDK 저장소의 `AGENTS.md` 파일들은 코딩 에이전트용으로 쓰여 있습니다.

## 지켜야 할 약관

가젯마다 `gadgets.muse.ai`에서 받은 SDK 토큰이 필요합니다. 굽거나 페어링하기 전에 Gadget SDK 약관을 읽으세요.
토큰은 비밀번호가 아니라 식별자입니다. 유출되면 폐기하고 다시 빌드하세요.
