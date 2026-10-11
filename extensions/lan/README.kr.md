[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](README.kr.md)

# LAN 확장

게이트웨이에서 집 네트워크의 장치에 닿습니다. TV, 스피커, 프린터처럼 로컬 HTTP API가 있는 장치와 Muse Home Link가 대상입니다.

## Linux

`--net=host`를 쓰면 컨테이너가 LAN에 바로 붙습니다.

```yaml
services:
  gateway:
    network_mode: host
```

## Windows / macOS (Docker Desktop)

호스트 네트워크를 쓸 수 없습니다. 컨테이너는 Desktop VM의 NAT 너머로 LAN을 보기 때문에 장치 검색 프로토콜(mDNS, SSDP)이 대부분 동작하지 않습니다. 방법은 둘입니다.

- 게이트웨이를 **direct 모듈**로 호스트에 직접 띄웁니다.
- 또는 LAN에 **Muse Home Link**(또는 집 네트워크 터널을 쓰는 ESP32 가젯)를 두고, Muse가 그것을 거쳐 장치에 닿게 합니다.

## Muse Home Link

Meta가 만든 가젯입니다. 집 Wi-Fi에 연결하는 USB-C 장치로, Muse가 TV·스피커·조명·프린터 등 HTTPS나 로컬 HTTP API가 있는 장치와 대화할 수 있게 합니다.
Philips Hue, Sonos, Apple TV, Google Nest, Samsung TV용 커뮤니티 스킬이 있습니다. Home Link 코드는 공개되어 있습니다([`../../gadgets/`](../../gadgets/README.kr.md) 참고).
