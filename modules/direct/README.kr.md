[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](README.kr.md)

# Direct 모듈 (호스트 설치)

Muse를 컨테이너 안에 가두지 않고 컴퓨터 전체에서 쓰게 하고 싶은 사용자를 위한 방식입니다. 게이트웨이가 호스트에서 직접 돌고, 같은 API를 제공합니다([`../container/gateway-spec.kr.md`](../container/gateway-spec.kr.md) 참고).

## 이럴 때 고르세요
- Muse가 내 파일, 도구, 스크립트에 직접 닿기를 원할 때
- 게이트웨이를 실행한 사용자 계정이 보는 것을 Muse도 본다는 점을 받아들일 때

## 이럴 때는 고르지 마세요
- Muse에게 넘기고 싶지 않은 것이 그 컴퓨터에 있을 때. 대신 container 모듈을 쓰세요.

## 설치
1. 호스트에 Tailscale을 설치하고 tailnet에 참여합니다.
2. 호스트에서 `gateway-spec.md`를 구현한 게이트웨이를 띄웁니다(기준 포트 `8730`). tailnet 인터페이스에만 바인딩합니다.
3. tailnet ACL에서 Muse 노드를 게이트웨이 포트에만 묶습니다.
4. tailnet IP:포트를 Muse에게 알려 주고, `bin/gateway-check.sh`로 확인합니다.

## 보안 참고
- 가능하면 권한이 낮은 전용 사용자 계정으로 게이트웨이를 실행하세요.
- 게이트웨이의 파일 루트는 여전히 지정한 폴더여야 합니다. 사용자가 정말 원하는 게 아니라면 "direct"가 "디스크 전체"를 뜻하지는 않습니다.
- 최상위 SKILL.md의 보안 참고가 모두 그대로 적용됩니다.
