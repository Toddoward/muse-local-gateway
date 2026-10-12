[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](usb-serial.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](usb-serial.kr.md)

# USB 시리얼 보드

내 컴퓨터에 꽂힌 보드(ESP32 계열, ESP8266, 그 밖의 USB 시리얼 장치)를 Muse가 빌드하고, 굽고, 읽게 합니다.
설치할 때 USB 질문에 **y**라고 답하면 켜집니다(`compose.usb.yaml`이 추가됨).

**안전한 이유:** 보드가 리셋되며 다시 잡혀도 보이도록 셸에 `/dev`를 넘기지만, cgroup 규칙이 **시리얼 장치만**
(`ttyACM` 166, `ttyUSB` 188) 허용합니다. 디스크, `/dev/mem`, 그 밖의 장치는 모두 막힙니다.

## Linux

바로 됩니다. 보드를 꽂으면 셸에 `/dev/ttyACM0`이나 `/dev/ttyUSB0`으로 나타납니다.

## Windows

Docker Desktop은 Windows의 USB 장치를 보지 못합니다. 설치 스크립트는 [usbipd-win](https://github.com/dorssel/usbipd-win)
(`winget install usbipd`)을 쓰고, 예약 작업 **`muse-usb-attach`**(`setup/usb-attach.ps1`, 로그인 시 + 5분마다)를 등록합니다.
이 작업은 다음을 합니다.

- 알려진 USB ID의 보드가 꽂히면 WSL로 넘깁니다: `303a` Espressif 네이티브 USB, `10c4` CP210x, `1a86` CH34x, `0403` FTDI
- 시리얼 드라이버(`cdc_acm cp210x ch341 ftdi_sio`)를 불러옵니다. Docker Desktop의 VM에는 udev가 없고,
  VM이 다시 시작되면 usbipd가 보드를 드라이버 **없이** 다시 붙이기 때문입니다.
- 보드가 리셋된 뒤 다시 붙입니다.

> **주의:** 같은 USB 칩이 Zigbee 동글, 3D 프린터, 일부 키보드의 펌웨어 포트에도 들어 있습니다. 이 ID를 가진
> 장치는 모두 Windows를 떠나 셸로 갑니다. 범위를 좁히려면 `setup/usb-attach.ps1`의 `$vids`를 고치세요.
> 기록: `setup/usb-attach.log`

## macOS

Docker Desktop으로는 불가능합니다. USB 작업은 Linux 컴퓨터(라즈베리 파이도 됩니다)에서 하세요.

## 장치 이름은?

| 보드 | 연결 | 나타나는 이름 |
|---|---|---|
| ESP32-S3 / C3 / C6 (USB 포트) | 네이티브 USB | `/dev/ttyACM0` |
| ESP32 DevKit, ESP8266 (NodeMCU, D1 mini) | CP210x / CH340 변환칩 | `/dev/ttyUSB0` |

## 문제 해결

- **Windows 장치 관리자에도 아무것도 안 뜸:** 충전 전용 케이블입니다. 다른 케이블을 쓰세요.
- **Windows에는 보이는데 셸에는 없음:** `usbipd list`에 *Attached*로 나와야 합니다. 그다음
  `docker compose exec bench ls /dev/ttyACM* /dev/ttyUSB*`. 붙어 있는데 없으면 30초 기다리거나(드라이버 재로드)
  `muse-usb-attach` 작업을 다시 시작하세요.
- **시리얼 모니터가 멈춤:** TTY가 없기 때문입니다.
  `stty -F /dev/ttyUSB0 115200 raw -echo; timeout 10 cat /dev/ttyUSB0`를 쓰세요.
