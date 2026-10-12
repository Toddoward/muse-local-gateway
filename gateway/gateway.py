"""Muse Local Gateway — file API.

GET /health                 -> {"ok": true}
PUT /files/<relative-path>  -> body written under SHARE_DIR -> 201 {"path", "bytes"}

Only the Tailscale sidecar may call PUT: `tailscale serve` forwards tailnet connections from the
sidecar's address, and the tailnet ACL decides which tailnet nodes get that far (tag:muse only).
Anything else is refused — there is no key to leak.

Stdlib only, so the same file runs in the container and directly on a host (direct/run.sh).
"""
import json
import os
import socket
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SHARE_DIR = os.environ.get("SHARE_DIR", "/share")
MAX_UPLOAD = int(os.environ.get("MAX_UPLOAD_MB", "200")) * 1024 * 1024
# Who counts as "the tailnet": the sidecar's compose name, or 127.0.0.1 when the host runs `tailscale serve`.
TAILNET_PEER = os.environ.get("TAILNET_PEER_HOST", "tailscale")
BIND = os.environ.get("BIND", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8730"))


def from_tailnet(client_ip, peer=None, resolve=socket.gethostbyname_ex):
    """True when the TCP peer is the Tailscale forwarder. Fails closed if the name can't be resolved."""
    try:
        return client_ip in resolve(peer or TAILNET_PEER)[2]
    except OSError:
        return False


def share_path(rel, root=None):
    """Absolute path for `rel` inside the share, or None if it would land anywhere else.

    Rejects empty paths, backslashes, absolute paths, NUL, `..` escapes, and the share itself.
    Symlinks are resolved first, so a link pointing outside is rejected too.
    """
    root = os.path.realpath(root or SHARE_DIR)
    if not rel or "\\" in rel or rel.startswith("/") or "\x00" in rel:
        return None
    full = os.path.realpath(os.path.join(root, rel))
    return full if full.startswith(root + os.sep) else None


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._json(200, {"ok": True})
        self._json(404, {"error": "not found"})

    def do_PUT(self):
        prefix = "/files/"
        path = urllib.parse.urlsplit(self.path).path
        if not path.startswith(prefix):
            return self._json(404, {"error": "not found"})
        if not from_tailnet(self.client_address[0]):
            return self._json(401, {"error": "tailnet only"})
        rel = urllib.parse.unquote(path[len(prefix):])
        full = share_path(rel)
        if not full:
            return self._json(400, {"error": "path must stay inside the shared folder"})
        length = self.headers.get("Content-Length")
        if length is None:
            return self._json(411, {"error": "Content-Length required"})
        try:
            length = int(length)
        except ValueError:
            return self._json(400, {"error": "bad Content-Length"})
        if length > MAX_UPLOAD:
            return self._json(413, {"error": f"file larger than {MAX_UPLOAD // (1024 * 1024)} MB"})

        os.makedirs(os.path.dirname(full), exist_ok=True)
        tmp = f"{full}.part-{uuid.uuid4().hex[:8]}"
        remaining = length
        # Write to a temp name and rename, so a half-sent file never shows up under its real name.
        with open(tmp, "wb") as f:
            while remaining:
                chunk = self.rfile.read(min(remaining, 1024 * 1024))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)
        if remaining:
            os.remove(tmp)
            return self._json(400, {"error": "connection closed before the whole file arrived"})
        os.replace(tmp, full)  # ponytail: same name overwrites; Muse date-stamps names it wants kept
        self._json(201, {"path": rel, "bytes": length})

    def log_message(self, fmt, *args):
        # One line per request, never bodies.
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main():
    os.makedirs(SHARE_DIR, exist_ok=True)
    print(f"muse-local-gateway files on {BIND}:{PORT}, share={SHARE_DIR}, tailnet peer={TAILNET_PEER}", flush=True)
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
