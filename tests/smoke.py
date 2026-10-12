"""End-to-end smoke test on a real Docker host (CI on Linux, or by hand on Windows/macOS).

  python tests/smoke.py [--usb] [--keep]

Brings the stack up under project "mlg-smoke" with tests/compose.smoke.yaml (curl stands in for
the Tailscale sidecar), then checks uploads, exec, and the isolated network from the bench's side.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["compose.yaml", "tests/compose.smoke.yaml"] + (["compose.usb.yaml"] if "--usb" in sys.argv else [])
LAN_OK, LAN_NO = "192.168.255.10", "192.168.255.11"  # private range (the proxy must decide), unlikely to exist
ENV = {**os.environ, "COMPOSE_FILE": "", "LAN_ALLOW": LAN_OK, "MUSE_SHARE": "./shared-smoke"}
failed = []


def dc(*args, check=True):
    cmd = ["docker", "compose", "-p", "mlg-smoke"] + sum((["-f", f] for f in FILES), []) + list(args)
    r = subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        sys.exit(f"FAILED: {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r.stdout.strip()


def curl(*args):
    return dc("exec", "-T", "tailscale", "curl", "-sS", "-m", "60", *args, check=False)


def run(cmd, timeout=60):
    out = curl("-X", "POST", "-H", "Content-Type: application/json", "http://bench:8731/exec",
               "-d", json.dumps({"cmd": cmd, "timeout": timeout, "wait": 50}))
    try:
        return json.loads(out)
    except ValueError:
        return {"stdout": "", "stderr": out, "exit_code": None}


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  -> {detail}"))
    if not ok:
        failed.append(name)


dc("up", "-d", "--build")
for _ in range(60):
    if '"ok": true' in curl("http://gateway:8730/health") and '"ok": true' in curl("http://bench:8731/health"):
        break
    time.sleep(2)

# files
r = curl("-X", "PUT", "--data-binary", "hello from smoke", "-w", " %{http_code}", "http://gateway:8730/files/smoke/hello.txt")
check("PUT file -> 201", r.endswith(" 201"), r)
r = curl("-X", "PUT", "--data-binary", "x", "-w", " %{http_code}", "--path-as-is", "http://gateway:8730/files/../escape.txt")
check("PUT outside the share -> 400/404", r.endswith(" 400") or r.endswith(" 404"), r)

# exec
v = run("cat /work/smoke/hello.txt")
check("bench sees the uploaded file", v.get("stdout") == "hello from smoke", v)
v = run("exit 7")
check("exit code comes back", v.get("exit_code") == 7, v)
v = run("cd /tmp && cp /app/bench.py /app/test_bench.py . && python3 test_bench.py", 120)
check("bench unit tests (Linux)", "ok" in v.get("stdout", ""), v)

# isolation (bench side)
v = run("curl -sS -m 8 --noproxy '*' -o /dev/null -w '%{http_code}' https://pypi.org/simple/ || echo blocked")
check("no direct internet (internal network)", "blocked" in v.get("stdout", ""), v)
v = run("curl -sS -m 20 -o /dev/null -w '%{http_code}' https://pypi.org/simple/")
check("internet through the proxy", v.get("stdout") == "200", v)
for target in ("http://192.168.0.1/", "http://host.docker.internal/", "http://100.100.100.100/"):
    v = run(f"curl -sS -m 8 -o /dev/null -w '%{{http_code}}' {target}")
    check(f"proxy refuses {target}", v.get("stdout") == "403", v)
v = run(f"curl -sS -m 8 -o /dev/null -w '%{{http_code}}' http://{LAN_NO}/")
check("lan-allow: unlisted device refused", v.get("stdout") == "403", v)
v = run(f"curl -sS -m 8 -o /dev/null -w '%{{http_code}}' http://{LAN_OK}/")
check("lan-allow: listed device passes the proxy", v.get("stdout") not in ("403", ""), v)
v = run("ls /var/run/docker.sock 2>&1; id -u")
check("no docker.sock in the bench", "No such file" in v.get("stdout", ""), v)
if "--usb" in sys.argv:
    v = run("ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null; head -c1 /dev/mem 2>&1 | head -1")
    check("usb: serial visible, /dev/mem denied", "tty" in v.get("stdout", "") and "not permitted" in v.get("stdout", ""), v)

if "--keep" not in sys.argv:
    dc("down", "-v")
print("\nALL PASSED" if not failed else f"\n{len(failed)} FAILED: {failed}")
sys.exit(1 if failed else 0)
