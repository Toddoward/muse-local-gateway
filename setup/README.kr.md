[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](README.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](README.kr.md)

# 설치 — OS를 고르세요

OS별 한 줄 설치입니다. 세 스크립트 모두 **container** 모듈(권장)을 설치합니다. direct 모듈은 따로 손으로 설치합니다([`../modules/direct/`](../modules/direct/README.kr.md) 참고).

## OS별로 되는 것

| | Linux | Windows | macOS |
|---|---|---|---|
| 컨테이너 게이트웨이 | ✅ | ✅ (Docker Desktop) | ✅ (Docker Desktop) |
| Tailscale | ✅ | ✅ | ✅ |
| USB 시리얼 연결 | ✅ (`--device`) | ⚠️ usbipd-win 필요 | ❌ (Docker Desktop 불가) |
| 컨테이너에서 블루투스 | ⚠️ (`--net=host`, privileged) | ❌ | ❌ |
| 컨테이너에서 LAN 장치 | ✅ (`--net=host`) | ⚠️ 제한적 | ⚠️ 제한적 |

자세한 내용: [`../extensions/`](../extensions/README.kr.md)

## 실행

**Linux:**
```bash
bash setup/linux/setup.sh
```

**Windows (관리자 PowerShell):**
```powershell
.\setup\windows\setup.ps1
```

**macOS:**
```bash
bash setup/mac/setup.sh
```

각 스크립트는 필요한 프로그램을 확인한 뒤 `modules/container/`를 띄웁니다.
그다음 tailnet IP:포트를 Muse에게 알려 주고 함께 확인하세요.
