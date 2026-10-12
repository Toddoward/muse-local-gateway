[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](direct.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](direct.kr.md)

# Direct 모듈 (실험적)

같은 게이트웨이와 셸을 컨테이너가 아니라 호스트에서 직접 돌립니다. Linux와 macOS용입니다.

**Muse는 이것을 실행한 사용자 계정의 권한을 그대로 갖습니다.** 그 계정이 닿는 모든 파일, 도구, 네트워크입니다.
컨테이너도, 네트워크 모드도, 프록시도, 웹 요청 기록도 없습니다. 먼저 [SECURITY.kr.md](../SECURITY.kr.md)를 읽으세요.
특별한 이유가 없으면 컨테이너 방식을 쓰세요.

좋은 이유의 예: Muse가 일하라고 둔 전용 기기(책상 위 라즈베리 파이)를, 권한이 낮은 전용 계정으로 쓸 때.

## 실행

호스트에 `python3`와 Tailscale이 있어야 하고, 로그인한 상태에서 이 기기에 `tag:muse-gw` 태그가 붙어 있어야 합니다
([`examples/tailnet-acl.hujson`](../examples/tailnet-acl.hujson) 참고).

```bash
MUSE_SHARE=~/muse-share ./direct/run.sh     # Ctrl+C로 둘 다 멈추고 serve 설정도 지웁니다
```

두 서버 모두 `127.0.0.1`에서만 듣고, `tailscale serve`가 tailnet의 `:8730`, `:8731`을 넘겨줍니다.
이 컴퓨터의 다른 프로그램도 두 서버를 부를 수 있습니다 — 그것이 "direct"의 의미입니다.
