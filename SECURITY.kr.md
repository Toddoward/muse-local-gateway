[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](SECURITY.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](SECURITY.kr.md)

# 보안

## 취약점 신고

GitHub의 비공개 신고 기능을 써 주세요: 이 저장소의 **Security → Report a vulnerability**.
아래 잠금장치를 우회할 수 있는 문제는 공개 이슈로 올리지 말아 주세요.

## 무엇을 막으려는가

현실적인 위협은 누군가 Tailscale을 뚫는 것이 아닙니다. **Muse가 속는 것**입니다.
웹페이지·파일·메시지에 숨은 지시(프롬프트 주입)가 Muse로 하여금 사용자가 시키지 않은 명령을 실행하게
만드는 경우입니다. 아래 내용은 모두 그런 일이 일어날 수 있다고 가정합니다.

## Muse를 조종하게 된 공격자가 할 수 있는 일

| | `isolated` (기본) | `lan-allow` | `open` | direct 모듈 |
|---|---|---|---|---|
| 공유 폴더의 파일 읽기·수정·삭제 | 가능 | 가능 | 가능 | 가능 |
| **공유 폴더 파일을 인터넷으로 보내기** | **가능** (프록시 경유) | 가능 | 가능 | 가능 |
| CPU·디스크·대역폭 사용 | 가능 | 가능 | 가능 | 가능 |
| USB 보드 다시 굽기 (USB를 켠 경우) | 가능 | 가능 | 가능 | 가능 |
| 지정한 LAN 기기에 접근 | 불가 | **가능**, HTTP(S) | 가능 | 가능 |
| 공유기·NAS·다른 LAN 기기에 접근 | 불가 | 불가 | **가능** | 가능 |
| 이 컴퓨터의 서비스에 접근 (`127.0.0.1` 전용 서비스까지¹) | 불가 | 불가 | **가능** | 가능 |
| 공유 폴더 밖의 파일 읽기 | 불가 | 불가 | 불가 | **가능** |
| 비밀값 읽기: Tailscale 키, 브라우저 데이터, SSH 키 | 불가 | 불가 | 불가 | **가능** |
| tailnet의 다른 기기에 접근 | 불가 | 불가 | **이 컴퓨터에도 Tailscale이 깔려 있으면 가능**² | 가능 |
| Docker 조작 / 호스트로 탈출 | 불가³ | 불가³ | 불가³ | 해당 없음 |

¹ Docker Desktop은 `host.docker.internal`을 호스트의 로컬 전용 서비스로 연결합니다.
² 게이트웨이의 tailnet 노드는 사이드카 하나이고, 셸은 그것을 경로로 쓸 수 없습니다. 하지만 `open` 모드의 셸은
이 컴퓨터의 네트워크를 그대로 씁니다 — 호스트에도 Tailscale이 깔려 있으면 그 경로까지 따라옵니다.
³ Docker 소켓 없음, 특권 권한 없음, 시리얼 장치만 허용. 컨테이너 탈출에는 커널이나 Docker의 취약점이
필요합니다 — 둘 다 최신으로 유지하세요.

## 그래서 실제로는

- **공유 폴더는 인터넷이 읽을 수 있다고 생각하세요.** 비밀값, 키, 개인 문서를 두지 마세요.
  Muse에게 필요한 것만 넣고, 만든 결과는 꺼내 가세요.
- **필요하지 않으면 `isolated`에 머무르세요.** HTTP 기기 몇 개라면 `lan-allow`로 충분합니다.
  `open`은 프록시로 안 되는 프로토콜(MQTT, UDP, mDNS)이 필요할 때만, 무엇이 열리는지 알고 고르세요.
- **Muse 기기에 `tag:muse`를 붙이세요.** 태그가 없는 Muse 기기는 *내* 기기로 취급되고, 기본 정책은 그 기기에
  tailnet 전체를 엽니다. 가장 중요한 한 단계입니다.
- **일회용·태그 붙은 인증 키**를 쓰세요(`tag:muse-gw`, 재사용 끔). `.env`와 `tailscale-state/`에는 인증 정보가
  들어 있습니다. 커밋하거나 공유하지 마세요(`.gitignore`가 이미 제외합니다).
- **한 번에 끊기:** Tailscale 관리 콘솔에서 Muse 기기를 지우거나, `docker compose down`.

## 어디를 보면 되나

```bash
docker compose logs bench                                   # Muse가 실행한 모든 명령 (출력은 아님)
docker compose logs gateway                                 # 모든 업로드 (경로와 결과, 내용은 아님)
docker compose exec egress tail /var/log/squid/access.log   # 셸이 보낸 모든 웹 요청
```

## 막지 못하는 것

- Muse 플랫폼 자체나 Muse 계정이 뚫리는 경우
- Tailscale 계정이 뚫리는 경우 (관리자는 ACL을 바꿀 수 있습니다)
- 사용자가 공유 폴더에 넣은 것 (위 참고)
