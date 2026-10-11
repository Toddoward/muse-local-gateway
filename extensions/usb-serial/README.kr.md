[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](README.kr.md)

# USB 시리얼 확장

게이트웨이 컨테이너가 USB 시리얼 장치에 닿게 합니다. ESP32 작업용 개발 스테이션입니다. 펌웨어를 빌드하고, 굽고, 시리얼 로그를 봅니다.

## Linux (전부 지원)

`docker-compose.yml`에 장치를 추가합니다.

```yaml
services:
  gateway:
    devices:
      - "/dev/ttyUSB0:/dev/ttyUSB0"
```

포트 찾기: `ls /dev/ttyUSB* /dev/ttyACM*`. 그다음 `docker compose up -d`를 다시 실행합니다.
이제 Muse가 게이트웨이에 그 포트로 도구 실행을 요청할 수 있습니다(예: `idf.py flash`, `idf.py monitor`).

## Windows (usbipd-win 사용)

Docker Desktop은 USB를 바로 넘겨주지 못합니다.

1. [usbipd-win](https://github.com/dorssel/usbipd-win)을 설치합니다.
2. `usbipd list`로 장치를 찾고, `usbipd attach --wsl --busid <id>`로 WSL2에 붙입니다.
3. Linux와 같은 방식으로 `--device` 항목을 추가합니다.

## macOS

Docker Desktop에서는 쓸 수 없습니다. 이 확장은 Linux 컴퓨터에서 쓰세요.

## Muse가 이걸로 하는 일

컨테이너에서 장치가 보이면, Muse가 게이트웨이의 셸(또는 게이트웨이가 제공하는 `system.run` 방식 명령)로 다음을 합니다.

- ESP32 펌웨어 빌드 (`idf.py build`)
- 굽기 (`idf.py -p /dev/ttyUSB0 flash`)
- 로그 보기 (`idf.py -p /dev/ttyUSB0 monitor`)

이것이 **개발 스테이션** 역할입니다. 구운 뒤의 ESP32는 Wi-Fi로 Muse와 직접 대화합니다([`../../gadgets/`](../../gadgets/README.kr.md) 참고). 동작 중에 컨테이너가 장치 통신을 중계하지 않습니다.
