[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](README.kr.md)

# Container 모듈 (권장)

게이트웨이가 Tailscale 사이드카와 함께 Docker 안에서 돕니다. Muse는 컨테이너 안만 볼 수 있고, 무엇이 보일지는 바인드 마운트가 정합니다.

## 구성

```yaml
# docker-compose.yml (이 폴더)
services:
  gateway:    # 파일 API. gateway-spec.md를 구현
  tailscale:  # tailnet에 들어가는 사이드카. 호스트는 tailnet에 들어가지 않음
```

## 빠른 시작

```bash
cd modules/container
docker compose up -d
# 안내가 나오면 tailnet에 참여하고, tailnet IP:포트를 Muse에게 알려 줍니다
```

## 무엇을 마운트할까

Muse가 쓸 폴더를 마운트합니다. 예:

```yaml
volumes:
  - ./shared:/data     # Muse가 쓸 수 있는 단 하나의 폴더
```

호스트 쪽 경로는 자유롭게 바꾸세요. `drop`/`work` 같은 이름을 고정하지 마세요.

## 승인 (두 번)

1. Muse가 `tailscale up`을 하면 링크가 나옵니다. 열어서 `muse` 장치를 tailnet에 들입니다.
2. Muse가 게이트웨이 주소에 처음 연결할 때 한 번 승인합니다. (같은 주소로의 이후 연결은 따로 묻지 않습니다.)

Muse 앱에서도 프로토콜을 허용해 주세요:
설정 > 권한 > 직접 네트워크 프로토콜

## 함께 보기

- [`gateway-spec.kr.md`](gateway-spec.kr.md) — 게이트웨이 이미지가 구현해야 할 API
- [`../../extensions/`](../../extensions/README.kr.md) — 컨테이너에서 USB/블루투스/LAN 쓰기
- [`../../setup/`](../../setup/README.kr.md) — OS별 한 줄 설치
