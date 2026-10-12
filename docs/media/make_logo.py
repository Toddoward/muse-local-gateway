"""Logos for Muse Local Gateway and Muse Gadget Forge — one continuous ribbon each.

  python docs/media/make_logo.py   -> docs/media/logo-gateway.svg, docs/media/logo-forge.svg

Rules (the author's brief):
  - continuous monoline: one unbroken line, one width, round caps at both ends
  - a 3D Z-axis trajectory drawn flat: where the line crosses itself, one layer passes behind the other
  - straight runs for the skeleton, short high-tension curves where the direction turns
  - depth from colour only: the colour flows along the trajectory (Muse blue -> cyan), and at each
    crossing the back layer is dark while the front layer is bright. No shadows.
No background: the marks sit on white and on dark pages alike.

gateway: `>_` — the chevron's lower arm runs on, loops round behind itself, and comes out as the underscore.
forge:   a gadget that speaks — down the outer voice arc, a tight fold, up the inner arc, round the device,
         and up its right side, which passes behind the top edge.
"""
import math
import os

W = 30                       # ribbon width on a 512 canvas
# Muse colour tokens (muse.ai CSS): blue-750, blue-550, blue-450, cyan-300, and a deep back tone
DEEP, BLUE, BRIGHT, CYAN, BACK = "#004BC7", "#0087F4", "#12A0FF", "#00C9EB", "#0B3A9E"


def grad(uid, gid, p, q, c0, c1):
    return (f'<linearGradient id="{uid}{gid}" x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
            f'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{c0}"/><stop offset="1" stop-color="{c1}"/></linearGradient>')


def stroke(uid, gid, d):
    return (f'<path d="{d}" fill="none" stroke="url(#{uid}{gid})" stroke-width="{W}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def unit(x, y):
    n = math.hypot(x, y)
    return x / n, y / n


def centred(defs, body, pts):
    """Translate the mark so its bounding box (points +- half the ribbon) sits in the middle of the canvas."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    dx = 256 - (min(xs) + max(xs)) / 2
    dy = 256 - (min(ys) + max(ys)) / 2
    return defs, f'<g transform="translate({dx:.1f} {dy:.1f})">{body}</g>'


def gateway(uid):
    a, tip = (140, 100), (300, 220)               # chevron: start, tip (upper arm at ~37 degrees)
    ang = math.radians(37)                        # lower arm mirrors it, heading down-left
    d2 = (-math.cos(ang), math.sin(ang))
    d1 = unit(tip[0] - a[0], tip[1] - a[1])
    k = 30                                        # how far back from the tip the turn starts (tension)
    p1 = (tip[0] - d1[0] * k, tip[1] - d1[1] * k)
    p2 = (tip[0] + d2[0] * k, tip[1] + d2[1] * k)
    yu, r = 330, 26                               # underscore line, loop radius
    # loop circle: tangent to the arm, top tangent to y=yu, centre up-left of the arm's travel
    n = (-math.sin(ang), -math.cos(ang))
    t = (yu + r - tip[1] - r * n[1]) / d2[1]
    e = (tip[0] + d2[0] * t, tip[1] + d2[1] * t)  # where the arm becomes the loop
    c = (e[0] + r * n[0], e[1] + r * n[1])
    top = (c[0], yu)
    end = (392, yu)
    defs = (grad(uid, "a", a, p1, DEEP, BRIGHT) + grad(uid, "b", p1, p2, BRIGHT, CYAN) + grad(uid, "c", p2, e, CYAN, BLUE)
            + grad(uid, "d", e, (c[0] - r, c[1]), BLUE, BACK) + grad(uid, "e", top, end, BACK, CYAN))
    back = (stroke(uid, "d", f"M{e[0]:.1f} {e[1]:.1f} A{r} {r} 0 1 1 {top[0]:.1f} {top[1]:.1f}")
            + stroke(uid, "e", f"M{top[0]:.1f} {top[1]:.1f} H{end[0]}"))
    front = (stroke(uid, "a", f"M{a[0]} {a[1]} L{p1[0]:.1f} {p1[1]:.1f}")
             + stroke(uid, "b", f"M{p1[0]:.1f} {p1[1]:.1f} Q{tip[0]} {tip[1]} {p2[0]:.1f} {p2[1]:.1f}")
             + stroke(uid, "c", f"M{p2[0]:.1f} {p2[1]:.1f} L{e[0]:.1f} {e[1]:.1f}"))
    h = W / 2
    pts = [(a[0] - h, a[1] - h), (tip[0] + h, tip[1]), (c[0] - r - h, c[1]), (c[0], c[1] + r + h), (end[0] + h, yu)]
    return centred(defs, back + front, pts)


def forge(uid):
    # a gadget that speaks: outer voice arc down, a tight fold, inner arc up, into the device's top edge,
    # round the device, and up its right side — which passes behind the top edge and ends there
    cx, cy = 286, 256                             # centre of the voice arcs (inner arc clears the device)
    r1, r2, sp = 58, 104, math.radians(50)        # inner/outer radius, half-spread
    def on(r, s):                                 # point on an arc; s=-1 top, +1 bottom
        return (cx + r * math.cos(sp), cy + s * r * math.sin(sp))
    o_top, o_bot, i_bot, i_top = on(r2, -1), on(r2, 1), on(r1, 1), on(r1, -1)
    hr = (r2 - r1) / 2                            # the fold: a half circle between the two arcs
    x0, y0, x1, y1, rr = 120, 181, 270, 331, 34   # the device
    defs = (grad(uid, "a", o_top, o_bot, CYAN, BRIGHT) + grad(uid, "b", o_bot, i_bot, BRIGHT, BLUE)
            + grad(uid, "c", i_bot, i_top, BLUE, BRIGHT) + grad(uid, "d", i_top, (x0, y1), BRIGHT, DEEP)
            + grad(uid, "e", (x0, y1), (x1, y0 - 22), DEEP, BACK))
    outer = f"M{o_top[0]:.1f} {o_top[1]:.1f} A{r2} {r2} 0 0 1 {o_bot[0]:.1f} {o_bot[1]:.1f}"
    fold = f"M{o_bot[0]:.1f} {o_bot[1]:.1f} A{hr} {hr} 0 0 1 {i_bot[0]:.1f} {i_bot[1]:.1f}"
    inner = f"M{i_bot[0]:.1f} {i_bot[1]:.1f} A{r1} {r1} 0 0 0 {i_top[0]:.1f} {i_top[1]:.1f}"
    # tangent at the inner arc's top points up-left; bend into the top edge heading left
    device = (f"M{i_top[0]:.1f} {i_top[1]:.1f} Q{x1 + 4} {y0} {x1 - rr} {y0} H{x0 + rr} Q{x0} {y0} {x0} {y0 + rr} "
              f"V{y1 - rr} Q{x0} {y1} {x0 + rr} {y1} H{x1 - rr} Q{x1} {y1} {x1} {y1 - rr}")
    rise = f"M{x1} {y1 - rr} V{y0 - 22}"          # behind the top edge, ending just above it
    body = (stroke(uid, "e", rise) + stroke(uid, "d", device) + stroke(uid, "c", inner)
            + stroke(uid, "b", fold) + stroke(uid, "a", outer))
    h = W / 2
    pts = [(x0 - h, y0 - 22 - h), (x0, y1 + h), (cx + r2 + h, cy), (o_top[0], o_top[1] - h), (o_bot[0], o_bot[1] + hr + h)]
    return centred(defs, body, pts)


def svg(kind, uid=None):
    uid = uid or f"lg{kind[0]}"
    defs, body = (gateway if kind == "gateway" else forge)(uid)
    return f'<defs>{defs}</defs>{body}'


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for kind, title in (("gateway", "Muse Local Gateway"), ("forge", "Muse Gadget Forge")):
        p = os.path.join(here, f"logo-{kind}.svg")
        open(p, "w", encoding="utf-8", newline="\n").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="{title} logo">{svg(kind)}</svg>\n')
        print(p, os.path.getsize(p), "bytes")
