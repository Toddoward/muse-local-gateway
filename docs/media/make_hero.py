"""README hero: an animated SVG (CSS keyframes, no JS), light/dark x English/Korean.

  python docs/media/make_hero.py        -> docs/media/hero-{en,kr}-{light,dark}.svg

Frame and motion follow the author's design rules (llm-wiki notes/design.md: margins 6.7% of the
long side, label -> title at the optical centre, few type sizes, one accent per scene, faint radial
lights, near-same two-colour radial text gradient, motion = fade 0.5 s / rise 14 px, nothing scales).
Colours are Muse's own tokens (muse.ai CSS: ai-gray scale, blue-650, colour families).
Loop (15 s): the logo opens large in the centre, shrinks into the top-left corner with the name, the four
scenes play with a small timeline (segments + "n / 4") in the bottom-left, then the logo returns to the
centre — the last frame equals the first. The logo's scale/move is the user's requested exception to
design.md A4 (no scaling). With prefers-reduced-motion the last scene shows, still, logo in the corner.
"""
import os
import re

from make_logo import svg as logo

THEMES = {
    # bg, t1..t4 = Muse ai-gray steps; accent = Muse blue; lights = Muse blue/pink/orange/shamrock
    "light": dict(bg="#FCFCFC", t1="#1F1F20", t1b="#30344A", t2="#4B4D4F", t3="#818487", t4="#ACAFB2", hair="#E0E2E4",
                  acc="#0069D9", accb="#0087F4", light_op=(.075, .05, .07, .055)),
    "dark": dict(bg="#1F1F20", t1="#E0E2E4", t1b="#BFCAE2", t2="#B5B7BB", t3="#818487", t4="#525456", hair="#383B3D",
                 acc="#70BEFF", accb="#91CCFF", light_op=(.14, .09, .12, .1)),
}
LIGHTS = ((0, 151, 255), (255, 74, 194), (255, 162, 81), (0, 208, 107))  # blue-500, pink-500, orange-300, shamrock-300
TEXT = {
    "en": [("IN THE CLOUD", "Muse works on a computer|of its own."),
           ("HANDS AND FEET", "Local Gateway lets it reach|the one beside you."),
           ("AT THE WORKBENCH", "A fenced shell, a shared folder,|the board on your desk."),
           ("ITS OWN EARS AND VOICE", "Muse can build the gadget|it listens and speaks through.")],
    "kr": [("IN THE CLOUD", "Muse는 자기만의|컴퓨터에서 일합니다."),
           ("HANDS AND FEET", "Local Gateway가 내 옆 컴퓨터에서|Muse의 손발이 되어 줍니다."),
           ("AT THE WORKBENCH", "울타리 친 셸과 공유 폴더,|그리고 책상 위의 보드."),
           ("ITS OWN EARS AND VOICE", "Muse는 자기 귀와 입이 될|가젯을 직접 만들 수 있습니다.")],
}
LABELS = {"en": ("MUSE SECURE VM", "YOUR COMPUTER", "shared folder"), "kr": ("MUSE SECURE VM", "내 컴퓨터", "공유 폴더")}
NAME = "Muse Local Gateway"
T0, T1 = 16.0, 90.7   # scenes play between these % of the 15 s loop; before/after = logo intro/outro
SEG = (16.0, 31.7, 47.4, 69.0, 90.7)


def remap(kf):
    """Scene keyframes were written on a 0..100 scale; squeeze them into T0..T1."""
    return re.sub(r"(\d+(?:\.\d+)?)%", lambda m: f"{T0 + float(m.group(1)) * (T1 - T0) / 100:.2f}%", kf)
W = [(0, 21), (21, 42), (42, 71), (71, 100)]          # scene windows, % of 12 s
SANS = "Pretendard, 'Pretendard Variable', system-ui, -apple-system, 'Segoe UI', 'Apple SD Gothic Neo', sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
FADE = 4.2  # % of 12 s = 0.5 s


def scene_kf(name, a, b, last):
    if last:
        return f"@keyframes {name}{{0%,{a}%{{opacity:0}}{a + FADE}%,96%{{opacity:1}}100%{{opacity:0}}}}"
    return f"@keyframes {name}{{0%,{a}%{{opacity:0}}{a + FADE}%,{b - FADE}%{{opacity:1}}{b}%,100%{{opacity:0}}}}"


def svg(theme, lang):
    c = THEMES[theme]
    vm, pc, folder = LABELS[lang]
    lights = "".join(
        f'<radialGradient id="l{i}" cx="{x}" cy="{y}" r="{r}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="rgb{rgb}" stop-opacity="{op}"/><stop offset=".62" stop-color="rgb{rgb}" stop-opacity="0"/></radialGradient>'
        for i, ((x, y, r), rgb, op) in enumerate(zip(((70, 40, 560), (1180, 90, 470), (1080, 540, 600), (180, 520, 420)), LIGHTS, c["light_op"])))
    css = [
        f".t{{font-family:{SANS}}} .m{{font-family:{MONO}}} .lb{{font-family:{MONO};letter-spacing:.08em}}",
        ".a{animation-duration:15s;animation-iteration-count:infinite;animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.7,.2,1)}",
        "@media (prefers-reduced-motion:reduce){.a{animation:none!important}}",
    ]
    heads = []
    for i, ((label, line), (a, b)) in enumerate(zip(TEXT[lang], W)):
        css.append(scene_kf(f"sc{i}", a, b, i == 3))
        lines = line.split("|")
        # label -> title (2u = 16 px), block centred on the optical centre (46% of 520 = 239)
        heads.append(
            f'<g class="a" style="animation-name:sc{i};opacity:{1 if i == 3 else 0}">'
            f'<text x="80" y="200" class="lb" font-size="15" fill="{c["t3"]}">{label}</text>'
            + "".join(f'<text x="80" y="{248 + 42 * k}" class="t" font-size="32" font-weight="600" fill="url(#tg)">{p}</text>'
                      for k, p in enumerate(lines)) + "</g>")
    css += [
        # 01 tasks run in parallel (drawn, not scaled)
        "@keyframes task{0%{stroke-dashoffset:184}18%,100%{stroke-dashoffset:var(--o)}}",
        # 02 the reach comes down (accent), your computer fades up
        "@keyframes reach{0%,21%{stroke-dashoffset:70;opacity:1}28%,42%{stroke-dashoffset:0;opacity:1}46%,100%{opacity:0}}",
        "@keyframes reachInk{0%,42%{opacity:0}46%,96%{opacity:1}100%{opacity:0}}",
        "@keyframes wake{0%,24%{opacity:.3}29%,96%{opacity:1}100%{opacity:.3}}",
        "@keyframes rise{0%,30%{opacity:0;transform:translateY(14px)}35%,96%{opacity:1;transform:translateY(0)}100%{opacity:0}}",
        # 03 build -> flash (accent on the bar), staged lines rise 14 px
        "@keyframes l1{0%,44%{opacity:0;transform:translateY(14px)}49%,96%{opacity:1;transform:translateY(0)}100%{opacity:0}}",
        "@keyframes l2{0%,58%{opacity:0;transform:translateY(14px)}63%,96%{opacity:1;transform:translateY(0)}100%{opacity:0}}",
        "@keyframes l3{0%,72%{opacity:0;transform:translateY(14px)}77%,96%{opacity:1;transform:translateY(0)}100%{opacity:0}}",
        "@keyframes bar{0%,48%{stroke-dashoffset:264}58%,100%{stroke-dashoffset:0}}",
        f"@keyframes barc{{0%,70%{{stroke:{c['acc']}}}73%,100%{{stroke:{c['t2']}}}}}",
        "@keyframes flow{0%,59%{opacity:0}62%,68%{opacity:1}71%,100%{opacity:.35}}",
        # 04 the gadget wakes and talks back to Muse (accent: the gadget)
        f"@keyframes lit{{0%,71%{{fill:{c['hair']}}}75%,96%{{fill:{c['acc']}}}100%{{fill:{c['hair']}}}}}",
        "@keyframes wave{0%,73%{opacity:0}79%{opacity:1}86%{opacity:.25}91%{opacity:1}96%,100%{opacity:0}}",
        "@keyframes back{0%,76%{opacity:0}82%,96%{opacity:1}100%{opacity:0}}",
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}",
    ]
    css = css[:3] + [remap(k) if k.startswith("@keyframes") and "blink" not in k else k for k in css[3:]]
    # intro/outro and the timeline (already on the 15 s scale)
    big, small = "translate(498px,88px) scale(.4)", "translate(68px,26px) scale(.11)"
    css += [
        f"@keyframes logo{{0%,10.7%{{transform:{big}}}16%,90.7%{{transform:{small}}}96%,100%{{transform:{big}}}}}",
        "@keyframes bigname{0%,9%{opacity:1}12%,93%{opacity:0}96%,100%{opacity:1}}",
        "@keyframes smallname{0%,14%{opacity:0}17%,89%{opacity:1}91%,100%{opacity:0}}",
        "@keyframes stage{0%,15%{opacity:0}18%,89.5%{opacity:1}92%,100%{opacity:0}}",
    ] + [f"@keyframes seg{i}{{0%,{a}%{{stroke-dashoffset:40}}{b}%,100%{{stroke-dashoffset:0}}}}" for i, (a, b) in enumerate(zip(SEG, SEG[1:]))]
    timeline = "".join(
        f'<line x1="{80 + 48 * i}" y1="464" x2="{120 + 48 * i}" y2="464" stroke="{c["hair"]}" stroke-width="3" stroke-linecap="round"/>'
        f'<line class="a" x1="{80 + 48 * i}" y1="464" x2="{120 + 48 * i}" y2="464" stroke="{c["t2"]}" stroke-width="3" stroke-linecap="round" '
        f'stroke-dasharray="40" style="animation-name:seg{i};animation-timing-function:linear;stroke-dashoffset:0"/>'
        for i in range(4)) + "".join(
        f'<text class="a m" x="284" y="469" font-size="13" fill="{c["t3"]}" style="animation-name:sc{i};opacity:{1 if i == 3 else 0}">{i + 1} / 4</text>'
        for i in range(4))
    tasks = "".join(
        f'<line x1="784" y1="{y}" x2="968" y2="{y}" stroke="{c["hair"]}" stroke-width="5" stroke-linecap="round"/>'
        f'<line class="a" x1="784" y1="{y}" x2="968" y2="{y}" stroke="{c["t2"]}" stroke-width="5" stroke-linecap="round" '
        f'stroke-dasharray="184" style="animation-name:task;animation-delay:{d}s;--o:{o};stroke-dashoffset:{o}"/>'
        for y, o, d in ((112, 64, 0), (126, 104, .25), (140, 30, .5)))
    waves = "".join(
        f'<path class="a" d="M{1094 + r * .2:.1f} {353 - r} A{r} {r} 0 0 1 {1094 + r * .2:.1f} {353 + r}" fill="none" stroke="{c["acc"]}" '
        f'stroke-width="2" stroke-linecap="round" style="animation-name:wave;animation-delay:{d}s"/>' for r, d in ((7, 0), (13, .12), (19, .24)))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 520" width="1200" height="520" role="img" aria-label="Muse reaches from its cloud computer to a workbench on your computer, where it can build its own gadget">
<style>{"".join(css)}</style>
<defs>{lights}
<radialGradient id="tg" cx="80" cy="200" r="560" gradientUnits="userSpaceOnUse"><stop offset=".35" stop-color="{c["t1"]}"/><stop offset="1" stop-color="{c["t1b"]}"/></radialGradient>
</defs>
<rect width="1200" height="520" rx="20" fill="{c["bg"]}"/>
{"".join(f'<rect width="1200" height="520" rx="20" fill="url(#l{i})"/>' for i in range(4))}
<g class="a" style="animation-name:stage">
{"".join(heads)}
{timeline}
<!-- Muse Secure VM -->
<rect x="700" y="72" width="300" height="96" rx="14" fill="none" stroke="{c["t4"]}" stroke-width="1.5"/>
<text x="716" y="94" class="lb" font-size="12" fill="{c["t3"]}">{vm}</text>
<circle cx="750" cy="126" r="13" fill="{c["t1"]}"/>
{tasks}
<!-- the reach: hands and feet -->
<line class="a" x1="850" y1="168" x2="850" y2="238" stroke="{c["acc"]}" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="70" style="animation-name:reach;opacity:0"/>
<line class="a" x1="850" y1="168" x2="850" y2="238" stroke="{c["t3"]}" stroke-width="1.5" style="animation-name:reachInk"/>
<!-- your computer -->
<g class="a" style="animation-name:wake">
<rect x="600" y="238" width="520" height="214" rx="16" fill="none" stroke="{c["t4"]}" stroke-width="1.5"/>
<text x="616" y="262" class="{'t' if lang == 'kr' else 'lb'}" font-size="12" fill="{c["t3"]}">{pc}</text>
<rect x="700" y="272" width="300" height="160" rx="10" fill="{c["bg"]}" stroke="{c["t2"]}" stroke-width="1.5"/>
<circle cx="716" cy="286" r="3" fill="{c["t4"]}"/><circle cx="726" cy="286" r="3" fill="{c["t4"]}"/><circle cx="736" cy="286" r="3" fill="{c["t4"]}"/>
<path d="M624 350 h20 l6 -8 h32 a5 5 0 0 1 5 5 v40 a5 5 0 0 1 -5 5 h-53 a5 5 0 0 1 -5 -5 z" fill="none" stroke="{c["t2"]}" stroke-width="1.5"/>
<rect class="a" x="642" y="355" width="20" height="25" rx="2.5" fill="{c["bg"]}" stroke="{c["t2"]}" stroke-width="1.2" style="animation-name:rise"/>
<text x="624" y="414" class="t" font-size="12" fill="{c["t3"]}">{folder}</text>
<line class="a" x1="1000" y1="353" x2="1030" y2="353" stroke="{c["t2"]}" stroke-width="1.5" stroke-dasharray="3 4" style="animation-name:flow;opacity:.35"/>
<rect x="1030" y="322" width="56" height="62" rx="8" fill="none" stroke="{c["t2"]}" stroke-width="1.5"/>
<rect class="a" x="1039" y="332" width="38" height="28" rx="4" fill="{c["acc"]}" style="animation-name:lit"/>
<text x="1030" y="404" class="lb" font-size="11" fill="{c["t3"]}">ESP32-S3</text>
{waves}
</g>
<g class="m" font-size="13">
<text class="a" x="716" y="314" fill="{c["t1"]}" style="animation-name:l1">$ idf.py build</text>
<line class="a" x1="716" y1="326" x2="980" y2="326" stroke="{c["hair"]}" stroke-width="4" stroke-linecap="round" style="animation-name:l1"/>
<line class="a" x1="716" y1="326" x2="980" y2="326" stroke="{c["t2"]}" stroke-width="4" stroke-linecap="round" stroke-dasharray="264" style="animation-name:bar,barc"/>
<text class="a" x="716" y="356" fill="{c["t1"]}" style="animation-name:l2">$ idf.py -p /dev/ttyACM0 flash</text>
<text class="a" x="716" y="380" fill="{c["t3"]}" style="animation-name:l3">link.main: Muse Gadget starting</text>
<text class="a" x="716" y="416" fill="{c["t2"]}" style="animation-name:blink;animation-duration:1s;animation-timing-function:steps(1)">$ _</text>
</g>
<!-- the gadget talks back to Muse over Wi-Fi -->
<path class="a" d="M1058 322 C 1090 250, 1070 150, 1000 128" fill="none" stroke="{c["t3"]}" stroke-width="1.5" stroke-dasharray="4 6" style="animation-name:back;opacity:1"/>
</g>
<!-- logo: centre -> corner -> centre -->
<g class="a" style="animation-name:logo;transform-box:view-box;transform-origin:0 0;transform:{small}">{logo("gateway", f"g{lang}{theme[0]}")}</g>
<text class="a t" x="600" y="320" text-anchor="middle" font-size="32" font-weight="600" letter-spacing="-0.025em" fill="url(#tg)" style="animation-name:bigname;opacity:0">{NAME}</text>
<text class="a t" x="124" y="68" font-size="17" font-weight="600" letter-spacing="-0.02em" fill="{c["t2"]}" style="animation-name:smallname;opacity:1">{NAME}</text>
</svg>
'''


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for theme in THEMES:
        for lang in TEXT:
            s = svg(theme, lang)
            # unique keyframe names, so heroes inlined into one page can't override each other
            names = set(re.findall(r"@keyframes ([\w-]+)", s))
            s = re.sub(r"@keyframes ([\w-]+)", lambda m: f"@keyframes {lang}{theme[0]}-{m.group(1)}", s)
            s = re.sub(r"animation-name:([\w,-]+)", lambda m: "animation-name:" + ",".join(
                f"{lang}{theme[0]}-{n}" if n in names else n for n in m.group(1).split(",")), s)
            p = os.path.join(here, f"hero-{lang}-{theme}.svg")
            open(p, "w", encoding="utf-8", newline="\n").write(s)
            print(p, os.path.getsize(p), "bytes")
