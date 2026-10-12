"""Smallest checks that fail if the gateway logic breaks. Run: python gateway/test_gateway.py"""
import http.client
import os
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(__file__))
import gateway  # noqa: E402


def test_from_tailnet():
    sidecar = lambda name: (name, [], ["172.19.0.3"])
    assert gateway.from_tailnet("172.19.0.3", "tailscale", sidecar)
    assert not gateway.from_tailnet("172.19.0.1", "tailscale", sidecar)  # Docker bridge = host side

    def unresolvable(name):
        raise OSError("no such host")
    assert not gateway.from_tailnet("172.19.0.3", "tailscale", unresolvable)  # fail closed


def test_share_path_stays_inside():
    root = tempfile.mkdtemp()
    ok = gateway.share_path("sub/out.png", root)
    assert ok == os.path.join(os.path.realpath(root), "sub", "out.png")
    for bad in ["", "../escape.txt", "sub/../../escape.txt", "/etc/passwd", "a\\b.txt", ".", "x\x00y"]:
        assert gateway.share_path(bad, root) is None, bad


def test_put_end_to_end():
    """Real server on loopback, peer = 127.0.0.1 (the direct-module setting)."""
    gateway.SHARE_DIR = tempfile.mkdtemp()
    gateway.TAILNET_PEER = "127.0.0.1"
    srv = ThreadingHTTPServer(("127.0.0.1", 0), gateway.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def put(path, body=b"hello", headers=None):
        c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=5)
        c.request("PUT", path, body=body, headers=headers or {})
        r = c.getresponse()
        return r.status, r.read()

    assert put("/files/a/b.txt")[0] == 201
    with open(os.path.join(gateway.SHARE_DIR, "a", "b.txt"), "rb") as f:
        assert f.read() == b"hello"
    assert put("/files/..%2Fescape.txt")[0] == 400
    assert put("/nope")[0] == 404
    gateway.TAILNET_PEER = "192.0.2.1"  # not us -> refused before touching the disk
    assert put("/files/c.txt")[0] == 401
    srv.shutdown()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
