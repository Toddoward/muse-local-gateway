"""The `>_` logo shared by Muse Local Gateway and Muse Gadget Forge.

  python docs/media/make_logo.py   -> docs/media/logo.svg

Same construction as the master in Figma (file "MuseLocalGateway", group "MuseLocalGateway Logo —
refined (Claude)"), designed by the author:
  - one continuous ribbon: down the chevron (straight arms, a rounded turn), a tight loop at the
    bottom-left, right along the back of the underscore, a flat fold, and back left along its front
  - the path is split where the underscore's back run passes behind the lower arm:
      A (behind)  crossing -> back run -> fold -> front face, in path order (the front face covers the back run)
      B (front)   crossing -> loop -> arms, in REVERSED order (so the arm sits on top at the crossing)
  - each part is a "gradient spline": a circle every 1 px along the path, coloured by its place on
    the line between the author's anchors (#004BC7 top, #0087F4 arm end, #0B3A9E loop, #12A0FF fold,
    #00C9EB end). Depth comes only from this colour and the layer order — no shadows.
"""
import math
import os

W = 44                                   # ribbon width before fitting
STEP = 1.0                               # one circle per px of path
HEIGHT = 312.8                           # fitted height of the mark (as in Figma)
ANCHORS = ("#004BC7", "#0087F4", "#0B3A9E", "#12A0FF", "#00C9EB")


def _norm(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def geometry():
    """Segments of the centre line: ('L', a, b) or ('A', centre, r, a0, a1). Index 4 ends at the crossing."""
    S, T = (44, 20), (150, 172)
    d1 = _norm((T[0] - S[0], T[1] - S[1]))
    d2 = _norm((-(T[0] - S[0]), T[1] - S[1]))              # lower arm mirrors the upper one
    a3 = math.radians(12.7)
    d3 = (math.cos(a3), math.sin(a3))                       # back run, slanting down-right
    rt, rl, rf = 46, 22, W / 2                              # chevron turn, loop, flat fold
    half = (math.pi - math.acos(d1[0] * d2[0] + d1[1] * d2[1])) / 2
    tt = rt / math.tan(half)
    tA, tB = _add(T, d1, -tt), _add(T, d2, tt)
    tc = _add(T, _norm(_add((-d1[0], -d1[1]), d2)), rt / math.sin(half))
    ang = lambda p, c: math.atan2(p[1] - c[1], p[0] - c[0])
    X = _add(T, d2, 150)                                    # where the back run passes behind the arm
    r2 = (-d3[0], -d3[1])
    th = math.acos(d2[0] * r2[0] + d2[1] * r2[1])
    lc = _add(X, _norm(_add(d2, r2)), rl / math.sin(th / 2))
    P1, P2 = _add(X, d2, rl / math.tan(th / 2)), _add(X, r2, rl / math.tan(th / 2))
    la0, la1 = ang(P1, lc), ang(P2, lc)
    while la1 < la0:
        la1 += 2 * math.pi                                  # the long way round the loop
    Q = _add(X, d3, (280 - X[0]) / d3[0])
    fc = _add(Q, (d3[1], -d3[0]), rf)
    yf = fc[1] - rf
    return [("L", S, tA), ("A", tc, rt, ang(tA, tc), ang(tB, tc)), ("L", tB, P1),
            ("A", lc, rl, la0, la1), ("L", P2, X),
            ("L", X, Q), ("A", fc, rf, ang(Q, fc), -math.pi / 2), ("L", (fc[0], yf), (X[0] + 2.05 * W, yf))]


def sample(segs):
    pts, marks = [], {}
    for si, s in enumerate(segs):
        if s[0] == "L":
            n = max(2, round(math.dist(s[1], s[2]) / STEP))
            run = [(s[1][0] + (s[2][0] - s[1][0]) * i / n, s[1][1] + (s[2][1] - s[1][1]) * i / n) for i in range(n + 1)]
        else:
            _, c, r, a0, a1 = s
            n = max(2, round(abs(a1 - a0) * r / STEP))
            run = [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), c[1] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
        pts.extend(run[1:] if pts else run)
        if si == 2:
            marks["arm_end"] = len(pts) - 1
        if si == 3:
            marks["loop"] = len(pts) - 1 - round(n * 0.35)
        if si == 4:
            marks["cross"] = len(pts) - 1
        if si == 6:
            marks["fold"] = len(pts) - 1 - round(n / 2)
    return pts, marks


def svg():
    pts, m = sample(geometry())
    lens = [0.0]
    for a, b in zip(pts, pts[1:]):
        lens.append(lens[-1] + math.dist(a, b))
    rgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    stops = list(zip((0, lens[m["arm_end"]], lens[m["loop"]], lens[m["fold"]], lens[-1]), map(rgb, ANCHORS)))

    def colour(l):
        for (l0, c0), (l1, c1) in zip(stops, stops[1:]):
            if l <= l1:
                k = (l - l0) / (l1 - l0)
                return "#%02X%02X%02X" % tuple(round(c0[i] + (c1[i] - c0[i]) * k) for i in range(3))
        return ANCHORS[-1]

    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, y0 = min(xs) - W / 2, min(ys) - W / 2
    k = HEIGHT / (max(ys) + W / 2 - y0)
    w = (max(xs) + W / 2 - x0) * k
    r = W / 2 * k

    def dot(i):
        return f'<circle cx="{(pts[i][0] - x0) * k:.2f}" cy="{(pts[i][1] - y0) * k:.2f}" r="{r:.2f}" fill="{colour(lens[i])}"/>'

    behind = "".join(dot(i) for i in range(m["cross"], len(pts)))
    front = "".join(dot(i) for i in range(m["cross"], -1, -1))
    return w, HEIGHT, f'<g>{behind}</g><g>{front}</g>'


if __name__ == "__main__":
    w, h, body = svg()
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.svg")
    open(p, "w", encoding="utf-8", newline="\n").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}" '
        f'role="img" aria-label="Muse Local Gateway logo">{body}</svg>\n')
    print(p, os.path.getsize(p), "bytes")
