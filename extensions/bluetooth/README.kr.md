[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](README.kr.md)

# 블루투스 확장

## 현재 상태: 제한적

컨테이너 안에서 블루투스를 쓰는 건 Linux에서만 현실적입니다. 그마저도 `--net=host`와 권한 상승이 필요해서, 컨테이너 모듈을 쓰는 이유인 샌드박스가 약해집니다.
Docker Desktop(Windows/macOS)에서는 사실상 쓸 수 없습니다.

## Linux (가능한 범위에서)

```yaml
services:
  gateway:
    network_mode: host
    privileged: true
    volumes:
      - /var/run/dbus:/var/run/dbus
```

무엇을 포기하는지 알고 쓰세요. `privileged`와 호스트 네트워크를 함께 쓰면 컨테이너 격리가 대부분 사라집니다.
블루투스가 꼭 필요하면 전용 컴퓨터에 direct 모듈을 쓰는 편이 낫습니다.

## 권장

블루투스 가젯은 **Muse Gadgets SDK의 페어링 절차**를 쓰세요.
가젯이 휴대폰의 Muse 앱과 Bluetooth LE로 페어링합니다([`../../gadgets/`](../../gadgets/README.kr.md) 참고). 컨테이너가 블루투스를 다룰 필요가 전혀 없습니다.
