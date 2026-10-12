"""Logos for Muse Local Gateway and Muse Gadget Forge — one continuous ribbon each.

  python docs/media/make_logo.py   -> docs/media/logo-gateway.svg, docs/media/logo-forge.svg

Rules (the author's brief):
  - continuous monoline: one unbroken line, one width, round caps at both ends
  - a 3D Z-axis trajectory drawn flat: where the line crosses itself, one layer passes behind the other
  - straight runs for the skeleton, short high-tension curves where the direction turns
  - depth from colour only: the colour flows along the trajectory (Muse blue -> cyan), and at each
    crossing the back layer is dark while the front layer is bright. No shadows.
No background: the marks sit on white and on dark pages alike.

How it is drawn: the centre line is sampled every few px; each short piece is stroked in the colour of
its place along the line (so the colour flows without seams), and pieces marked "back" are drawn
before the "front" ones, which is what puts one layer behind the other at a crossing.

gateway: `>_` — the chevron's lower arm runs on, loops round behind itself, and comes out as the underscore.
forge:   a gadget that speaks — down the outer voice arc, a tight fold, up the inner arc, round the device,
         and up its right side, which passes behind the top edge.
"""
import math
import os

W = 60          # ribbon width on a 512 canvas (~16% of the mark)
STEP = 4        # sampling step along the centre line, px
# Muse colour tokens (muse.ai CSS): blue-750, blue-550, blue-450, cyan-300, and a deep back tone
DEEP, BLUE, BRIGHT, CYAN, BACK = "#004BC7", "#0087F4", "#12A0FF", "#00C9EB", "#0B3A9E"


# --- geometry -------------------------------------------------------------------------------------
def line(p, q):
    n = max(1, int(math.dist(p, q) / STEP))
    return [(p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n) for i in range(n + 1)]


def quad(p, c, q):
    n = max(2, int((math.dist(p, c) + math.dist(c, q)) / STEP))
    return [((1 - t) ** 2 * p[0] + 2 * (1 - t) * t * c[0] + t * t * q[0],
             (1 - t) ** 2 * p[1] + 2 * (1 - t) * t * c[1] + t * t * q[1]) for t in (i / n for i in range(n + 1))]


def arc(c, r, a0, a1):
    n = max(2, int(abs(a1 - a0) * r / STEP))
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), c[1] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def unit(x, y):
    n = math.hypot(x, y)
    return x / n, y / n


# --- colour ---------------------------------------------------------------------------------------
def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def mix(stops, f):
    """Colour at fraction f of the line; stops = [(fraction, hex), ...] ascending."""
    for (f0, c0), (f1, c1) in zip(stops, stops[1:]):
        if f <= f1:
            k = 0 if f1 == f0 else (f - f0) / (f1 - f0)
            k = k * k * (3 - 2 * k)               # smoothstep: no visible kinks where stops meet
            a, b = rgb(c0), rgb(c1)
            return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))
    return stops[-1][1]


def marks(runs):
    """Index where each run starts, plus the cumulative length at every sample."""
    pts = [p for run, _ in runs for p in run]
    lens = [0.0]
    for a, b in zip(pts, pts[1:]):
        lens.append(lens[-1] + math.dist(a, b))
    starts = [0]
    for run, _ in runs:
        starts.append(starts[-1] + len(run))
    return starts, lens


def ribbon(runs, stops):
    """runs = [(points, 'back'|'front'), ...] in path order -> SVG pieces, back layer first."""
    pts = [(p, layer) for run, layer in runs for p in run]
    _, lens = marks(runs)
    total = lens[-1]
    pieces = {"back": [], "front": []}
    for i in range(len(pts) - 1):
        (a, la), (b, lb) = pts[i], pts[i + 1]
        if math.dist(a, b) < 1e-6:
            continue
        colour = mix(stops, (lens[i] + lens[i + 1]) / 2 / total)
        pieces[lb if la == lb else "front"].append(
            f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{colour}"/>')
    return f'<g stroke-width="{W}" stroke-linecap="round">' + "".join(pieces["back"]) + "".join(pieces["front"]) + "</g>"


def fit(body, runs, box=440):
    """Centre the mark on the 512 canvas and scale it down to fit box x box (ribbon width included)."""
    h = W / 2
    pts = [p for run, _ in runs for p in run]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs) - h, max(xs) + h, min(ys) - h, max(ys) + h
    s = min(1, box / (x1 - x0), box / (y1 - y0))
    return f'<g transform="translate(256 256) scale({s:.4f}) translate({-(x0 + x1) / 2:.1f} {-(y0 + y1) / 2:.1f})">{body}</g>'


# --- marks ----------------------------------------------------------------------------------------
def gateway():
    a, tip = (150, 104), (312, 226)               # chevron: start, tip (arms at ~37 degrees)
    ang = math.radians(37)
    d1, d2 = unit(tip[0] - a[0], tip[1] - a[1]), (-math.cos(ang), math.sin(ang))
    k = 44                                        # the turn at the tip starts this far back (tension)
    p1, p2 = (tip[0] - d1[0] * k, tip[1] - d1[1] * k), (tip[0] + d2[0] * k, tip[1] + d2[1] * k)
    yu, r = 352, 44                               # underscore line, loop radius
    n = (-math.sin(ang), -math.cos(ang))          # loop centre lies up-left of the arm
    t = (yu + r - tip[1] - r * n[1]) / d2[1]
    e = (tip[0] + d2[0] * t, tip[1] + d2[1] * t)  # the arm becomes the loop here
    c = (e[0] + r * n[0], e[1] + r * n[1])
    a0 = math.atan2(e[1] - c[1], e[0] - c[0])
    runs = [(line(a, p1), "front"), (quad(p1, tip, p2), "front"), (line(p2, e), "front"),
            (arc(c, r, a0, 1.5 * math.pi), "back"), (line((c[0], yu), (424, yu)), "back")]
    s, lens = marks(runs)
    f = lambda i: lens[min(i, len(lens) - 1)] / lens[-1]
    stops = [(0, DEEP), (f((s[1] + s[2]) // 2), CYAN), (f(s[3]), BLUE), (f(s[4]), BACK), (1, CYAN)]
    return fit(ribbon(runs, stops), runs)


def forge():
    cx, cy = 304, 256                             # centre of the voice arcs
    r1, r2, sp = 70, 146, math.radians(46)        # inner/outer radius (fold = half the gap), half-spread
    x0, y0, x1, y1, rr = 104, 172, 268, 340, 46   # the device
    hr = (r2 - r1) / 2
    fc = (cx + (r1 + hr) * math.cos(sp), cy + (r1 + hr) * math.sin(sp))   # centre of the fold
    i_top = (cx + r1 * math.cos(sp), cy - r1 * math.sin(sp))
    runs = [(arc((cx, cy), r2, -sp, sp), "front"),                       # outer voice arc, down
            (arc(fc, hr, sp, sp + math.pi), "front"),                    # the fold
            (arc((cx, cy), r1, sp, -sp), "front"),                       # inner arc, up
            (quad(i_top, (x1 + 4, y0), (x1 - rr, y0)), "front"),         # into the device's top edge
            (line((x1 - rr, y0), (x0 + rr, y0)), "front"),
            (quad((x0 + rr, y0), (x0, y0), (x0, y0 + rr)), "front"),
            (line((x0, y0 + rr), (x0, y1 - rr)), "front"),
            (quad((x0, y1 - rr), (x0, y1), (x0 + rr, y1)), "front"),
            (line((x0 + rr, y1), (x1 - rr, y1)), "front"),
            (quad((x1 - rr, y1), (x1, y1), (x1, y1 - rr)), "front"),
            (line((x1, y1 - rr), (x1, y0 - 40)), "back")]                # up behind the top edge
    s, lens = marks(runs)
    f = lambda i: lens[min(i, len(lens) - 1)] / lens[-1]
    stops = [(0, CYAN), (f(s[1]), BRIGHT), (f(s[2]), BLUE), (f(s[3]), BRIGHT),
             (f(s[7]), DEEP), (f(s[10]), BLUE), (1, BACK)]
    return fit(ribbon(runs, stops), runs)


def svg(kind, uid=None):
    """The mark as SVG elements (no ids — every piece carries its own colour, so copies never clash)."""
    return gateway() if kind == "gateway" else forge()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for kind, title in (("gateway", "Muse Local Gateway"), ("forge", "Muse Gadget Forge")):
        p = os.path.join(here, f"logo-{kind}.svg")
        open(p, "w", encoding="utf-8", newline="\n").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="{title} logo">{svg(kind)}</svg>\n')
        print(p, os.path.getsize(p), "bytes")
