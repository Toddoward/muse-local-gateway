"""Generates the README hero: an animated SVG (CSS keyframes, no JS) in light/dark x English/Korean.

  python docs/media/make_hero.py        -> docs/media/hero-{en,kr}-{light,dark}.svg

Colors follow Muse's own sites (gadgets.muse.ai paper/ink, muse.ai blue). One accent per scene.
With prefers-reduced-motion the SVG shows its last scene, still.
"""
import os
import re

THEMES = {
    "light": dict(paper="#F2F0EC", card="#FFFFFF", ink="#16161D", mute="#62625D", faint="#D9D7D1", grid="#E4E2DC", accent="#0069D9"),
    "dark": dict(paper="#16161D", card="#1B222E", ink="#F2F0EC", mute="#AEB4C2", faint="#303440", grid="#242A36", accent="#80ADFF"),
}
TEXT = {
    "en": [("01 / IN THE CLOUD", "Muse works on|a computer of its own."),
           ("02 / HANDS AND FEET", "Local Gateway lets it reach|the computer right beside you."),
           ("03 / AT THE WORKBENCH", "A fenced shell, a shared folder,|and the board on your desk."),
           ("04 / ITS OWN EARS AND VOICE", "Muse just built the gadget|it will listen and speak through.")],
    "kr": [("01 / IN THE CLOUD", "Muse는 자기만의|컴퓨터에서 일합니다."),
           ("02 / HANDS AND FEET", "Local Gateway가 내 옆의 컴퓨터에서|Muse의 손발이 되어 줍니다."),
           ("03 / AT THE WORKBENCH", "울타리 친 셸과 공유 폴더,|그리고 책상 위의 보드."),
           ("04 / ITS OWN EARS AND VOICE", "Muse가 자기 귀와 입이 될|가젯을 직접 만들었습니다.")],
}
LABELS = {"en": ("MUSE SECURE VM", "YOUR COMPUTER", "shared folder"), "kr": ("MUSE SECURE VM", "내 컴퓨터", "공유 폴더")}
# scene windows in % of the 12 s loop
W = [(0, 21), (21, 42), (42, 71), (71, 100)]
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "system-ui, -apple-system, 'Segoe UI', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"


def show(name, a, b, fade=2.5, base=0.0):
    """Keyframes: invisible, fade in at a, out at b (b=100 stays to the end, then fades for the loop)."""
    if b >= 100:
        return f"@keyframes {name}{{0%,{a}%{{opacity:{base}}}{a + fade}%,95%{{opacity:1}}100%{{opacity:{base}}}}}"
    return f"@keyframes {name}{{0%,{a}%{{opacity:0}}{a + fade}%,{b - fade}%{{opacity:1}}{b}%,100%{{opacity:0}}}}"


def svg(theme, lang):
    c = THEMES[theme]
    vm, pc, folder = LABELS[lang]
    css = [
        f".m{{font-family:{MONO};letter-spacing:.12em}} .s{{font-family:{SANS}}}",
        ".x{transform-box:fill-box;transform-origin:left center} .c{transform-box:fill-box;transform-origin:center} .a{animation-duration:12s;animation-iteration-count:infinite;animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.7,.2,1)}",
        "@media (prefers-reduced-motion:reduce){.a{animation:none!important}}",
    ]
    scenes = []
    for i, ((label, line), (a, b)) in enumerate(zip(TEXT[lang], W)):
        css.append(show(f"sc{i}", a, b))
        final = 1 if i == 3 else 0  # the still frame is scene 4
        scenes.append(f'<g class="a" style="animation-name:sc{i};opacity:{final}">'
                      f'<text x="48" y="58" class="m" font-size="13" fill="{c["ink"]}">{label}</text>'
                      + "".join(f'<text x="48" y="{86 + 24 * k}" class="s" font-size="17" fill="{c["mute"]}">{part}</text>' for k, part in enumerate(line.split("|"))) + "</g>")
    css += [
        # 01: Muse breathing, tasks running in parallel
        "@keyframes breathe{0%,100%{transform:scale(1);opacity:.25}50%{transform:scale(1.25);opacity:.05}}",
        "@keyframes task1{0%{transform:scaleX(0)}20%,100%{transform:scaleX(1)}} @keyframes task2{0%,4%{transform:scaleX(0)}21%,100%{transform:scaleX(1)}} @keyframes task3{0%,8%{transform:scaleX(0)}20%,100%{transform:scaleX(1)}}",
        # 02: the reach comes down; your computer wakes up
        "@keyframes reach{0%,21%{stroke-dashoffset:118;opacity:1}29%,42%{stroke-dashoffset:0;opacity:1}44%,100%{stroke-dashoffset:0;opacity:0}}",
        "@keyframes reachInk{0%,42%{opacity:0}44%,95%{opacity:1}100%{opacity:0}}",
        "@keyframes wake{0%,24%{opacity:.35}30%,100%{opacity:1}}",
        "@keyframes drop{0%,31%{transform:translateY(-58px);opacity:0}33%{opacity:1}38%,100%{transform:translateY(0);opacity:1}}",
        # 03: build, flash
        show("t1", 44, 100, 2), show("t2", 58, 100, 2), show("t3", 66, 100, 2),
        "@keyframes bar{0%,46%{transform:scaleX(0)}56%,100%{transform:scaleX(1)}}",
        f"@keyframes barColor{{0%,70%{{fill:{c['accent']}}}72%,100%{{fill:{c['ink']}}}}}",
        "@keyframes flow{0%,58%{stroke-dashoffset:24;opacity:0}59%{opacity:1}66%{stroke-dashoffset:0;opacity:1}68%,100%{stroke-dashoffset:0;opacity:.4}}",
        # 04: the gadget comes alive and talks back to Muse
        f"@keyframes lit{{0%,71%{{fill:{c['faint']}}}73%,95%{{fill:{c['accent']}}}100%{{fill:{c['faint']}}}}}",
        "@keyframes wave{0%,72%{opacity:0;transform:scale(.6)}80%{opacity:1;transform:scale(1)}88%{opacity:.2;transform:scale(1.15)}96%,100%{opacity:0}}",
        "@keyframes back{0%,74%{opacity:0}82%,95%{opacity:1}100%{opacity:0}}",
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}",
    ]
    waves = "".join(
        f'<path class="a" d="M{948 + r} {392 - r} A{r} {r} 0 0 1 {948 + r} {392 + r}" fill="none" stroke="{c["accent"]}" '
        f'stroke-width="2" stroke-linecap="round" style="animation-name:wave;animation-delay:{d}s;transform-box:fill-box;transform-origin:left center"/>'
        for r, d in ((10, 0), (20, .15), (30, .3)))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 520" width="1200" height="520" role="img" aria-label="Muse reaches from its cloud computer to a workbench on your computer and builds its own gadget">
<style>{"".join(css)}</style>
<defs><pattern id="g" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{c["grid"]}"/></pattern></defs>
<rect width="1200" height="520" rx="24" fill="{c["paper"]}"/><rect width="1200" height="520" rx="24" fill="url(#g)"/>
{"".join(scenes)}
<g transform="translate(130 0)">
<!-- the cloud -->
<rect x="430" y="40" width="340" height="112" rx="16" fill="{c["paper"]}" stroke="{c["faint"]}" stroke-width="1.5" stroke-dasharray="6 6"/>
<text x="450" y="64" class="m" font-size="10.5" fill="{c["mute"]}">{vm}</text>
<circle class="a c" cx="510" cy="106" r="26" fill="{c["ink"]}" style="animation-name:breathe;animation-duration:3s;opacity:.15"/>
<circle cx="510" cy="106" r="17" fill="{c["ink"]}"/>
{"".join(f'<rect x="556" y="{y}" width="180" height="6" rx="3" fill="{c["faint"]}"/><rect class="a x" x="556" y="{y}" width="{w}" height="6" rx="3" fill="{c["ink"]}" style="animation-name:{n}"/>' for y, w, n in ((90, 120, "task1"), (104, 84, "task2"), (118, 150, "task3")))}
<!-- the reach: hands and feet -->
<path class="a" d="M600 152 V270" stroke="{c["accent"]}" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="118" style="animation-name:reach;opacity:0"/>
<path class="a" d="M600 152 V270" stroke="{c["ink"]}" stroke-width="1.5" style="animation-name:reachInk"/>
<!-- your computer -->
<g class="a" style="animation-name:wake">
<rect x="250" y="226" width="760" height="276" rx="20" fill="none" stroke="{c["faint"]}" stroke-width="1.5" stroke-dasharray="6 6"/>
<text x="270" y="250" class="{'s' if lang == 'kr' else 'm'}" font-size="{12 if lang == 'kr' else 10.5}" fill="{c["mute"]}">{pc}</text>
<rect x="430" y="270" width="340" height="196" rx="12" fill="{c["card"]}" stroke="{c["ink"]}" stroke-width="1.5"/>
<circle cx="448" cy="286" r="3.5" fill="{c["faint"]}"/><circle cx="460" cy="286" r="3.5" fill="{c["faint"]}"/><circle cx="472" cy="286" r="3.5" fill="{c["faint"]}"/>
<path d="M290 392 h30 l8 -10 h44 a6 6 0 0 1 6 6 v58 a6 6 0 0 1 -6 6 h-76 a6 6 0 0 1 -6 -6 z" fill="{c["card"]}" stroke="{c["ink"]}" stroke-width="1.5"/>
<rect class="a" x="314" y="398" width="28" height="34" rx="3" fill="{c["paper"]}" stroke="{c["ink"]}" stroke-width="1.2" style="animation-name:drop"/>
<text x="290" y="478" class="s" font-size="12" fill="{c["mute"]}">{folder}</text>
<path class="a" d="M770 404 H850" stroke="{c["ink"]}" stroke-width="1.5" stroke-dasharray="4 4" style="animation-name:flow"/>
<rect x="850" y="362" width="76" height="84" rx="10" fill="{c["card"]}" stroke="{c["ink"]}" stroke-width="1.5"/>
<rect class="a" x="862" y="376" width="52" height="40" rx="6" fill="{c["accent"]}" style="animation-name:lit"/>
<text x="850" y="478" class="m" font-size="10.5" fill="{c["mute"]}">ESP32-S3</text>
{waves}
</g>
<g class="m" font-size="13.5">
<text class="a" x="450" y="322" fill="{c["ink"]}" style="animation-name:t1">$ idf.py build</text>
<rect x="450" y="334" width="300" height="5" rx="2.5" fill="{c["faint"]}" class="a" style="animation-name:t1"/>
<rect class="a x" x="450" y="334" width="300" height="5" rx="2.5" fill="{c["ink"]}" style="animation-name:bar,barColor"/>
<text class="a" x="450" y="370" fill="{c["ink"]}" style="animation-name:t2">$ idf.py -p /dev/ttyACM0 flash</text>
<text class="a" x="450" y="398" fill="{c["mute"]}" style="animation-name:t3">link.main: Muse Gadget starting</text>
<text class="a" x="450" y="438" fill="{c["ink"]}" style="animation-name:blink;animation-duration:1s;animation-timing-function:steps(1)">$ _</text>
</g>
<!-- the gadget talks back to Muse over Wi-Fi -->
<path class="a" d="M888 362 C 900 250, 860 120, 772 100" fill="none" stroke="{c["mute"]}" stroke-width="1.5" stroke-dasharray="5 6" style="animation-name:back;opacity:1"/>
</g>
</svg>
'''


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for theme in THEMES:
        for lang in TEXT:
            p = os.path.join(here, f"hero-{lang}-{theme}.svg")
            s = svg(theme, lang)
            # unique keyframe names, so several heroes inlined in one page can't override each other
            names = set(re.findall(r"@keyframes ([\w-]+)", s))
            s = re.sub(r"@keyframes ([\w-]+)", lambda m: f"@keyframes {lang}{theme[0]}-{m.group(1)}", s)
            s = re.sub(r"animation-name:([\w,-]+)", lambda m: "animation-name:" + ",".join(
                f"{lang}{theme[0]}-{n}" if n in names else n for n in m.group(1).split(",")), s)
            open(p, "w", encoding="utf-8", newline="\n").write(s)
            print(p, os.path.getsize(p), "bytes")
