"""Muse Local Gateway — bench: runs shell commands for Muse inside its own container.

POST   /exec       {"cmd", "cwd"?, "timeout"?, "wait"?}
                   Runs `sh -c cmd`. Waits up to `wait` seconds: finished -> full result,
                   still running -> {"status": "running", "id", ...}. Poll with GET.
GET    /exec/<id>  status + output so far
DELETE /exec/<id>  kill the job (whole process group)
GET    /health

Only the Tailscale forwarder may call this (tailnet ACL: tag:muse -> tag:muse-gw:8731).
No secrets live here and no host port is published. Stdlib only; Linux/macOS (process groups).
"""
import json
import os
import signal
import socket
import subprocess
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8731"))
TAILNET_PEER = os.environ.get("TAILNET_PEER_HOST", "tailscale")
CAP = int(os.environ.get("OUTPUT_CAP_KB", "1024")) * 1024  # per stream, per job
DEFAULT_CWD = os.environ.get("WORK_DIR", "/work")
BIND = os.environ.get("BIND", "0.0.0.0")
DEFAULT_TIMEOUT, MAX_TIMEOUT = 60, 3600
DEFAULT_WAIT, MAX_WAIT = 30, 50  # stay under common HTTP client timeouts
KEEP = 50  # finished jobs kept for GET; ponytail: in memory, lost on restart
TIMEOUT_EXIT = 124  # same as coreutils `timeout`


def from_tailnet(client_ip, peer=None, resolve=socket.gethostbyname_ex):
    """True when the TCP peer is the Tailscale sidecar. Fails closed. Same rule as gateway.py."""
    try:
        return client_ip in resolve(peer or TAILNET_PEER)[2]
    except OSError:
        return False


class Tail:
    """Keeps the LAST `cap` bytes — build errors are at the end, not the start."""

    def __init__(self, cap=None):
        self.cap = cap or CAP
        self.buf = bytearray()
        self.truncated = False

    def add(self, b):
        self.buf += b
        if len(self.buf) > self.cap:
            del self.buf[:len(self.buf) - self.cap]
            self.truncated = True

    def text(self):
        return bytes(self.buf).decode("utf-8", errors="replace")


class Job:
    def __init__(self, cmd, cwd, timeout, cap=None):
        self.id = uuid.uuid4().hex[:12]
        self.cmd = cmd
        self.started = time.time()
        self.timed_out = self.killed = False
        self.out, self.err = Tail(cap), Tail(cap)
        self.done = threading.Event()
        # New session = own process group, so kill reaches children (idf.py spawns many).
        self.proc = subprocess.Popen(
            ["sh", "-c", cmd], cwd=cwd, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
        )
        self._readers = [threading.Thread(target=self._pump, args=p, daemon=True)
                         for p in ((self.proc.stdout, self.out), (self.proc.stderr, self.err))]
        for t in self._readers:
            t.start()
        threading.Thread(target=self._watch, args=(timeout,), daemon=True).start()

    @staticmethod
    def _pump(pipe, tail):
        for chunk in iter(lambda: pipe.read1(65536), b""):
            tail.add(chunk)

    def _watch(self, timeout):
        try:
            self.proc.wait(timeout)
        except subprocess.TimeoutExpired:
            self.timed_out = True
            self.kill()
            self.proc.wait()
        for t in self._readers:
            t.join(2)  # a daemon that escaped the group may hold the pipe; don't hang on it
        self.done.set()

    def kill(self):
        try:
            os.killpg(self.proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    def view(self):
        v = {"id": self.id, "stdout": self.out.text(), "stderr": self.err.text(),
             "truncated": self.out.truncated or self.err.truncated,
             "elapsed": round(time.time() - self.started, 1)}
        if not self.done.is_set():
            return {**v, "status": "running"}
        status = "killed" if self.killed else "timeout" if self.timed_out else "done"
        code = TIMEOUT_EXIT if self.timed_out else self.proc.returncode
        return {**v, "status": status, "exit_code": code}


jobs = {}  # id -> Job, insertion order
jobs_lock = threading.Lock()


def add_job(job):
    with jobs_lock:
        jobs[job.id] = job
        finished = [j for j in jobs.values() if j.done.is_set()]
        for j in finished[:max(0, len(jobs) - KEEP)]:
            del jobs[j.id]


def _clamp(value, default, hi):
    try:
        return max(0, min(float(value if value is not None else default), hi))
    except (TypeError, ValueError):
        return None


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _job(self):
        job = jobs.get(self.path[len("/exec/"):]) if self.path.startswith("/exec/") else None
        if not job:
            self._json(404, {"error": "no such job"})
        return job

    def _allowed(self):
        if from_tailnet(self.client_address[0]):
            return True
        self._json(401, {"error": "tailnet only"})
        return False

    def do_GET(self):
        if self.path == "/health":
            return self._json(200, {"ok": True})
        if self._allowed() and (job := self._job()):
            self._json(200, job.view())

    def do_DELETE(self):
        if self._allowed() and (job := self._job()):
            if not job.done.is_set():
                job.killed = True
                job.kill()
                job.done.wait(5)
            self._json(200, job.view())

    def do_POST(self):
        if not self._allowed():
            return
        if self.path != "/exec":
            return self._json(404, {"error": "not found"})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except (ValueError, TypeError):
            return self._json(400, {"error": "invalid JSON"})
        cmd = req.get("cmd") if isinstance(req, dict) else None
        if not isinstance(cmd, str) or not cmd.strip():
            return self._json(400, {"error": "cmd must be a non-empty string"})
        cwd = req.get("cwd") or DEFAULT_CWD
        if not os.path.isdir(cwd):
            return self._json(400, {"error": f"cwd does not exist: {cwd}"})
        timeout = _clamp(req.get("timeout"), DEFAULT_TIMEOUT, MAX_TIMEOUT)
        wait = _clamp(req.get("wait"), DEFAULT_WAIT, MAX_WAIT)
        if not timeout or wait is None:
            return self._json(400, {"error": f"timeout 1..{MAX_TIMEOUT}, wait 0..{MAX_WAIT} (seconds)"})

        job = Job(cmd, cwd, timeout)
        add_job(job)
        # Commands are logged (audit trail if Muse is ever tricked); their output never is.
        print(f"exec {job.id} cwd={cwd} timeout={timeout:.0f} cmd={cmd[:300]!r}", flush=True)
        job.done.wait(wait)
        self._json(200, job.view())

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main():
    print(f"muse-local-gateway bench on {BIND}:{PORT}, cwd={DEFAULT_CWD}, tailnet peer={TAILNET_PEER}", flush=True)
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
