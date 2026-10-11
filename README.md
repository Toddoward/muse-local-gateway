# Muse Local Gateway

Muse AI가 사용자의 로컬 머신(홈 PC, 랩박스, 홈서버)에 직접 접근할 수 있게 하는 게이트웨이.

중계 서버 없이 Tailscale을 통해 파일을 주고받고, 명령을 실행하고, 로컬 데이터를 다룬다.
포트 포워딩도, 공인 노출도 필요 없다. 사용자가 Muse에게 보여줄 범위를 직접 정한다.

> 상태: 모듈형 드래프트 (2026-10-08). K12 실배포는 검증 완료.
> 배포판 모듈은 신규 작성되어 현장 테스트 대기 중.

## 왜 필요한가

- Muse는 클라우드 VM에서 동작한다. 사용자의 PC에 있는 파일, USB 장치, 로컬 모델에 닿으려면 통로가 필요하다.
- 이 게이트웨이가 그 통로다. 사용자의 머신에 작은 서버를 띄우면, Muse가 Tailscale 망을 통해 직접 파일을 올리고 결과를 받아간다.

## 모듈 선택

| | Container (권장) | Direct |
|---|---|---|
| 방식 | Docker + Tailscale sidecar | 호스트에 직접 설치 |
| Muse가 보는 범위 | 바인드 마운트한 폴더만 | 컴퓨터 전체 (사용자 선택) |
| 격리 | 샌드박스 | 없음 |
| 시작 | `modules/container/` | `modules/direct/` |

OS별 설치: `setup/` (Windows / Linux / macOS)

## 구성 요소

- **`modules/container/`** — 권장 방식. 게이트웨이 컨테이너 + Tailscale sidecar의 Docker Compose, 게이트웨이 API 스펙
- **`modules/direct/`** — 호스트 직접 설치. Muse에게 머신 전체를 맡기고 싶은 경우
- **`setup/`** — OS별 원커맨드 설치. USB 패스스루 등 OS별 capability matrix 포함
- **`extensions/`** — 연결 후 확장: USB-시리얼, 블루투스, LAN 장치 접근
- **`gadgets/`** — Muse Gadgets SDK 연동 가이드 (되는 것과 안 되는 것)
- **`bin/`** — Muse 측 도구: `gateway-check.sh`, `gateway-put.sh`, `gateway-exec.sh`

## 게이트웨이 API (요약)

| 항목 | 내용 |
|---|---|
| 파일 업로드 | `PUT /files/<상대경로>` |
| 상태 확인 | `GET /health` → `{"ok": true}` |
| 인증 | tailnet에서 없음. tailnet ACL이 Muse 노드를 게이트웨이 포트로 고정 |

상세 스펙: `modules/container/gateway-spec.md`

## 보안 원칙

- 명령 실행은 **별도의 secrets-free 컨테이너**에서 (파일 게이트웨이와 분리)
- tailnet ACL은 Muse 노드를 각 컨테이너 포트로만 고정
- 경로 탐색 공격 (`..`, 절대경로) 거부
- 네트워크 격리 모드는 설치 시 선택 (기본값 `isolated` 권장)

## AI용 문서

Muse가 이 스킬을 사용하는 방법은 [SKILL.md](SKILL.md) 참조.
