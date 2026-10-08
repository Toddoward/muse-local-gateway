# Gateway API spec

The minimal HTTP API a gateway must implement. Verified against the
reference K12 deployment.

## Endpoints

### `GET /health`
Returns `{"ok": true}` (may include extra fields like
`"relay_configured"`). Used to verify reachability before uploading.

### `PUT /files/<relative-path>`
Stores the request body as a file.

- `<relative-path>`: relative only. Reject `..`, absolute paths (leading
  `/`), and backslashes with `400`.
- `Content-Length` header required; missing → `411`.
- Enforce a max body size (reference: 200MB); over → `413`.
- Parent directories are created as needed.
- Same name overwrites.
- Success: `201` with `{"path": "<relative-path>", "bytes": <size>}`.

## Auth
None on the tailnet. The gateway trusts tailnet identity:
- The tailnet ACL pins Muse's node to the gateway port.
- Tailscale cryptographically authenticates every peer.

Do not add password/key auth on top — it duplicates what the tailnet
already proves. Do not log request bodies.

## Binding
Listen on the container's port (reference: `8730`). The Tailscale sidecar
exposes it via `tailscale serve`. No host port needs publishing.

## Reference behavior
```
$ curl -X PUT --data-binary @a.txt http://<tailnet-ip>:8730/files/a.txt
{"path": "a.txt", "bytes": 123}     # HTTP 201

$ curl http://<tailnet-ip>:8730/health
{"ok": true}                        # HTTP 200
```

## Exec endpoint (reference)

File-only gateways may omit this. When command execution is wanted, run
it in a **separate container** from the file gateway (K12 reference:
`muse-bench`), with no secrets and network isolation (see the skill's
network modes).

### `POST /exec`
Runs `cmd` via `sh -c`. Request: `{"cmd": "...", "cwd": "/work",
"timeout": 60, "wait": 30}` (`cmd` required; `timeout` 1–3600, default 60;
`wait` 0–50, default 30). Finishes within `wait` → result; otherwise
`{"status": "running", "id": "<id>"}`.

Response:
`{"id","status":"done"|"running"|"timeout"|"killed","exit_code","stdout","stderr","truncated","elapsed"}`.

### `GET /exec/<id>` — poll (output so far while running)
### `DELETE /exec/<id>` — kill the whole process group

Output cap: stdout/stderr 1 MB each; over → drop the head, keep the tail
(`truncated: true`). Timeout kills the process group (`exit_code: 124`).
Finished-job history may be memory-only (a restart wipes it).
