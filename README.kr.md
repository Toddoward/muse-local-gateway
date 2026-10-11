[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](README.kr.md)

# Muse Local Gateway

Muse AI가 내 컴퓨터(홈 PC, 실험용 PC, 홈서버)에 직접 닿을 수 있게 해 주는 게이트웨이입니다.

중계 서버 없이 Tailscale로 파일을 주고받고, 명령을 실행하고, 로컬 데이터를 다룹니다. 포트 포워딩도, 공인 IP 노출도 필요 없습니다. Muse에게 보여 줄 범위는 사용자가 직접 정합니다.

> **상태:** 모듈형 초안 (2026-10-08). K12 실배포는 검증을 마쳤습니다.
> 배포용 모듈은 새로 작성했고 현장 테스트를 기다리고 있습니다.

## 왜 필요한가

- Muse는 클라우드 VM에서 동작합니다. 사용자 PC에 있는 파일, USB 장치, 로컬 모델에 닿으려면 통로가 필요합니다.
- 이 게이트웨이가 그 통로입니다. 내 컴퓨터에 작은 서버를 띄우면, Muse가 Tailscale 망으로 직접 파일을 올리고 결과를 받아 갑니다.

## 모듈 선택

| | Container (권장) | Direct |
|---|---|---|
| 방식 | Docker + Tailscale 사이드카 | 호스트에 직접 설치 |
| Muse가 보는 범위 | 바인드 마운트한 폴더만 | 컴퓨터 전체 (사용자 선택) |
| 격리 | 샌드박스 | 없음 |
| 시작 | [`modules/container/`](modules/container/README.kr.md) | [`modules/direct/`](modules/direct/README.kr.md) |

OS별 설치: [`setup/`](setup/README.kr.md) (Windows / Linux / macOS)

## 구성

- **[`modules/container/`](modules/container/README.kr.md)** — 권장 방식. 게이트웨이 컨테이너와 Tailscale 사이드카의 Docker Compose, 게이트웨이 API 명세
- **[`modules/direct/`](modules/direct/README.kr.md)** — 호스트에 직접 설치. Muse에게 컴퓨터 전체를 맡기고 싶을 때
- **[`setup/`](setup/README.kr.md)** — OS별 한 줄 설치. USB 연결 등 OS마다 되는 것을 정리한 표 포함
- **[`extensions/`](extensions/README.kr.md)** — 연결한 뒤의 확장: USB 시리얼, 블루투스, LAN 장치 접근
- **[`gadgets/`](gadgets/README.kr.md)** — Muse Gadgets SDK와 어떻게 맞물리는지 (되는 것과 안 되는 것)
- **`bin/`** — Muse 쪽 도구: `gateway-check.sh`, `gateway-put.sh`, `gateway-exec.sh`

## 게이트웨이 API (요약)

| 항목 | 내용 |
|---|---|
| 파일 올리기 | `PUT /files/<상대경로>` |
| 상태 확인 | `GET /health` → `{"ok": true}` |
| 인증 | tailnet 안에서는 없음. tailnet ACL이 Muse 노드를 게이트웨이 포트에만 묶음 |

전체 명세: [`modules/container/gateway-spec.kr.md`](modules/container/gateway-spec.kr.md)

## 보안 원칙

- 명령 실행은 파일 게이트웨이와 분리된 **비밀값 없는 별도 컨테이너**에서
- tailnet ACL은 Muse 노드를 각 컨테이너 포트에만 묶음
- 경로 탈출(`..`, 절대경로) 거부
- 네트워크 격리 모드는 설치할 때 선택 (기본값이자 권장: `isolated`)

## AI용 문서

Muse가 이 스킬을 쓰는 방법: [SKILL.md](SKILL.md)
