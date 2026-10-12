"""Smallest checks for bench.py. Linux/macOS only (process groups). Run: python3 bench/test_bench.py"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import bench  # noqa: E402


def test_tail_keeps_the_end():
    t = bench.Tail(cap=5)
    t.add(b"abc")
    t.add(b"defgh")
    assert t.text() == "defgh" and t.truncated


def test_job_done():
    j = bench.Job("echo hi; echo err >&2; exit 3", "/tmp", 10)
    assert j.done.wait(5)
    v = j.view()
    assert (v["status"], v["exit_code"], v["stdout"], v["stderr"]) == ("done", 3, "hi\n", "err\n")


def test_job_timeout_kills_children():
    j = bench.Job("sleep 30 & sleep 30; wait", "/tmp", 1)
    assert j.done.wait(5)
    v = j.view()
    assert (v["status"], v["exit_code"]) == ("timeout", 124), v


def test_job_kill():
    j = bench.Job("echo started; sleep 30", "/tmp", 60)
    time.sleep(0.3)
    assert j.view()["status"] == "running"
    j.killed = True
    j.kill()
    assert j.done.wait(5)
    v = j.view()
    assert v["status"] == "killed" and v["stdout"] == "started\n"


def test_from_tailnet_fails_closed():
    def unresolvable(name):
        raise OSError
    assert bench.from_tailnet("172.19.0.3", "tailscale", lambda n: (n, [], ["172.19.0.3"]))
    assert not bench.from_tailnet("172.19.0.1", "tailscale", lambda n: (n, [], ["172.19.0.3"]))
    assert not bench.from_tailnet("172.19.0.3", "tailscale", unresolvable)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
