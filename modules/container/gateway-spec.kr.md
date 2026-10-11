[![English](https://img.shields.io/badge/lang-English-lightgrey?style=flat-square)](gateway-spec.md)
[![한국어](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-111111?style=flat-square)](gateway-spec.kr.md)

# 게이트웨이 API 명세

게이트웨이가 구현해야 하는 최소 HTTP API입니다. K12 기준 배포에서 검증했습니다.

## 엔드포인트

### `GET /health`
`{"ok": true}`를 돌려줍니다(`"relay_configured"` 같은 필드가 더 있어도 됩니다). 파일을 올리기 전에 연결을 확인하는 데 씁니다.

### `PUT /files/<relative-path>`
요청 본문을 파일로 저장합니다.

- `<relative-path>`: 상대경로만 받습니다. `..`, 절대경로(앞에 `/`), 백슬래시는 `400`으로 거부합니다.
- `Content-Length` 헤더 필수. 없으면 `411`
- 본문 크기 상한을 둡니다(기준: 200MB). 넘으면 `413`
- 상위 폴더는 필요하면 만듭니다.
- 같은 이름이면 덮어씁니다.
- 성공: `201`과 `{"path": "<relative-path>", "bytes": <size>}`

## 인증
tailnet 안에서는 없습니다. 게이트웨이는 tailnet 신원을 믿습니다.
- tailnet ACL이 Muse 노드를 게이트웨이 포트에만 묶습니다.
- Tailscale이 모든 상대를 암호학적으로 인증합니다.

그 위에 비밀번호나 키 인증을 덧붙이지 마세요. tailnet이 이미 증명하는 것을 중복할 뿐입니다. 요청 본문은 로그에 남기지 마세요.

## 바인딩
컨테이너 포트에서 듣습니다(기준: `8730`). Tailscale 사이드카가 `tailscale serve`로 이 포트를 노출합니다. 호스트 포트를 열 필요가 없습니다.

## 기준 동작
```
$ curl -X PUT --data-binary @a.txt http://<tailnet-ip>:8730/files/a.txt
{"path": "a.txt", "bytes": 123}     # HTTP 201

$ curl http://<tailnet-ip>:8730/health
{"ok": true}                        # HTTP 200
```

## 명령 실행 엔드포인트 (기준 구현)

파일만 다루는 게이트웨이는 생략해도 됩니다. 명령 실행이 필요하면 파일 게이트웨이와 **분리된 컨테이너**에서 돌리세요(K12 기준: `muse-bench`). 비밀값을 두지 않고 네트워크를 격리합니다(스킬의 네트워크 모드 참고).

### `POST /exec`
`cmd`를 `sh -c`로 실행합니다. 요청: `{"cmd": "...", "cwd": "/work", "timeout": 60, "wait": 30}`
(`cmd` 필수, `timeout` 1–3600·기본 60, `wait` 0–50·기본 30). `wait` 안에 끝나면 결과를, 아니면 `{"status": "running", "id": "<id>"}`를 돌려줍니다.

응답:
`{"id","status":"done"|"running"|"timeout"|"killed","exit_code","stdout","stderr","truncated","elapsed"}`

### `GET /exec/<id>` — 상태 조회 (실행 중이면 지금까지의 출력)
### `DELETE /exec/<id>` — 프로세스 그룹 전체 종료

출력 상한: stdout/stderr 각각 1 MB. 넘으면 앞부분을 버리고 끝부분을 남깁니다(`truncated: true`). 시간 초과 시 프로세스 그룹을 종료합니다(`exit_code: 124`).
끝난 작업 기록은 메모리에만 있어도 됩니다(재시작하면 지워짐).
