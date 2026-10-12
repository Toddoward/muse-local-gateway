"""Logos for Muse Local Gateway and Muse Gadget Forge: one continuous line each, in Muse blue.

  python docs/media/make_logo.py   -> docs/media/logo-gateway.svg, docs/media/logo-forge.svg

No background — they sit on white and on dark pages alike. The stroke is Muse blue with a faint radial
shade (blue-650 -> blue-500, light from the top-left) for a little depth.
  gateway: a box (Muse's computer) whose floor runs on out of it and steps down — beside you
  forge:   a closed chip; the line goes round it and leaves as a voice that fades
"""
import os

STROKE = 22


def defs(uid):
    return (f'<radialGradient id="{uid}" cx="120" cy="110" r="520" gradientUnits="userSpaceOnUse">'
            f'<stop offset=".2" stop-color="#0069D9"/><stop offset="1" stop-color="#0097FF"/></radialGradient>')


def mark(kind, uid):
    s = f'fill="none" stroke="url(#{uid})" stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "gateway":
        # open on the right above the floor; the floor continues out, steps down, and runs on
        return (f'<path transform="translate(-31 -5)" d="M300 214 V170 A38 38 0 0 0 262 132 H170 A38 38 0 0 0 132 170 '
                f'V270 A38 38 0 0 0 170 308 H330 A38 38 0 0 1 368 346 V352 A38 38 0 0 0 406 390 H442" {s}/>')
    # forge: a closed square chip — the line starts on its right side, goes all the way round, and leaves
    # from the same point as a voice that fades
    return (f'<path transform="translate(-25 4)" d="M270 252 V210 A38 38 0 0 0 232 172 H148 A38 38 0 0 0 110 210 V294 '
            f'A38 38 0 0 0 148 332 H232 A38 38 0 0 0 270 294 V252 H290 C 306 252, 306 202, 322 202 '
            f'C 344 202, 344 302, 366 302 C 388 302, 388 228, 406 228 C 424 228, 424 252, 440 252 H452" {s}/>')


def svg(kind, uid=None):
    uid = uid or f"lg{kind}"
    return f'<defs>{defs(uid)}</defs>{mark(kind, uid)}'


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for kind, title in (("gateway", "Muse Local Gateway"), ("forge", "Muse Gadget Forge")):
        p = os.path.join(here, f"logo-{kind}.svg")
        open(p, "w", encoding="utf-8", newline="\n").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="{title} logo">{svg(kind)}</svg>\n')
        print(p, os.path.getsize(p), "bytes")
