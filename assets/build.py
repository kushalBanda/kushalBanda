"""Builds the README's SVGs from assets/src. Run: python3 assets/build.py

GitHub strips CSS and scripts from READMEs, so every designed surface is a self-contained SVG: fonts and images are
embedded as data URIs, motion is CSS inside the SVG, and every animation stops under prefers-reduced-motion.
The visual world is kushalbanda.com's (kushalBanda/sites, docs/portfolio/DESIGN.md).
"""

import base64
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"

GREY, INK, PAPER, BLUE = "#737677", "#1C1D20", "#FFFFFF", "#455CE9"
GLOBE = "#999C9D"
EASE = "cubic-bezier(0.16, 1, 0.3, 1)"


def data_uri(name: str, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode((SRC / name).read_bytes()).decode()


def fonts() -> str:
    src = data_uri("GeneralSans-Regular.woff2", "font/woff2")
    return f"@font-face{{font-family:'General Sans';font-weight:400;src:url({src}) format('woff2')}}"


def svg(w: int, h: int, label: str, style: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">'
        f"<title>{label}</title>"
        f"<style>{style}"
        "text{font-family:'General Sans',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;font-weight:400}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
        f"</style>{body}</svg>\n"
    )


def write(name: str, content: str) -> None:
    (ROOT / name).write_text(content)
    print(f"{name}: {len(content.encode()) / 1024:.0f} KB")


# ---------- Header: the grey name band ----------
# The name at 250px measures 1418px wide in General Sans with -0.03em tracking (measured in Chromium);
# textLength pins it so the loop is seamless whatever the renderer's metrics.
NAME_W, NAME_PX = 1418, 250
PAD = 0.12 * NAME_PX  # padding-inline around each name, as on the site
DASH_W, DASH_M = 0.55 * NAME_PX, 0.2 * NAME_PX
UNIT = PAD + NAME_W + PAD + DASH_M + DASH_W + DASH_M


def globe(cx: float, cy: float) -> str:
    return (
        f'<circle cx="{cx}" cy="{cy}" r="52" fill="{GLOBE}"/>'
        f'<g transform="translate({cx - 26} {cy - 26}) scale(1.625)" fill="none" stroke="{PAPER}" stroke-width="1.5">'
        '<circle cx="16" cy="16" r="12"/><ellipse class="meridian" cx="16" cy="16" rx="5.5" ry="12"/>'
        '<path d="M4 16h24M6.2 9.5h19.6M6.2 22.5h19.6"/></g>'
    )


def header(small: bool = False) -> str:
    """Desktop: pill left, role right, name along the bottom. Phones: role on top, pill, then the name."""
    w, h, base = (720, 600, 560) if small else (1280, 460, 432)
    track = ""
    for i in range(3):
        x = i * UNIT
        track += (
            f'<text x="{x + PAD:.1f}" y="0" font-size="{NAME_PX}" letter-spacing="-7.5" '
            f'textLength="{NAME_W}" lengthAdjust="spacing">Kushal Banda</text>'
            f'<rect x="{x + PAD + NAME_W + PAD + DASH_M:.1f}" y="{-0.36 * NAME_PX:.1f}" '
            f'width="{DASH_W:.1f}" height="{0.07 * NAME_PX:.1f}"/>'
        )
    style = (
        fonts()
        + f"@keyframes slide{{to{{transform:translateX(-{UNIT:.1f}px)}}}}"
        + ".track{animation:slide 22s linear infinite}"
        + "@keyframes globe{0%{transform:scaleX(1)}50%{transform:scaleX(-1)}100%{transform:scaleX(1)}}"
        + ".meridian{transform-box:fill-box;transform-origin:center;animation:globe 5s linear infinite}"
    )
    # Ink half-pill flush with the left edge: city in three lines, then the grey globe.
    py, ph, pw = (236, 160, 460) if small else (56, 160, 460)
    pill = (
        f'<path d="M0 {py}H{pw - ph / 2}a{ph / 2} {ph / 2} 0 0 1 0 {ph}H0Z" fill="{INK}"/>'
        f'<text fill="{PAPER}" font-size="30"><tspan x="48" y="{py + 40}">Based</tspan>'
        f'<tspan x="48" y="{py + 80}">in Hyderabad,</tspan><tspan x="48" y="{py + 120}">India</tspan></text>'
        + globe(pw - ph / 2, py + ph / 2)
    )
    rx, ry = (48, 40) if small else (830, 36)
    role = (
        f'<g transform="translate({rx} {ry})" fill="none" stroke="{PAPER}" stroke-width="2">'
        '<path d="M2 2l26 26M28 7.5V28H7.5"/></g>'
        f'<text fill="{PAPER}" font-size="{40 if small else 38}"><tspan x="{rx}" y="{ry + 82}">AI Engineer</tspan>'
        f'<tspan x="{rx}" y="{ry + 130}">designing products</tspan>'
        f'<tspan x="{rx}" y="{ry + 178}">for agent users</tspan></text>'
    )
    body = (
        f'<rect x="-4" y="-4" width="{w + 8}" height="{h + 8}" fill="{GREY}"/>{pill}{role}'
        # Phones set the name smaller so most frames show it whole (about 1.3x the band's width).
        f'<g transform="translate(0 {base}) scale({0.64 if small else 1})">'
        f'<g class="track" fill="{PAPER}">{track}</g></g>'
    )
    return svg(w, h, "Kushal Banda. AI Engineer designing products for agent users. Based in Hyderabad, India.", style, body)


# ---------- Product cards: the site's hover preview, laid flat ----------
# Four cards sit inline at a quarter of the column each. Phones get the same cards with the foot type
# set larger (a card is about 85px wide there) and a shorter kind line.
CW = 400
GAP = 12


def card(label, bg, ink, sub, name, kind, media, line=(), line_ink=None, style="", gap=GAP, small=False) -> str:
    """Desktop foot: name, a two-line note on what the product does, then kind and year.
    Phones drop the note (a card is about 85px wide there) and set name and kind larger."""
    foot = 318 if small else 360  # the hairline above the card's name
    h = 460 if small else 548
    if small:
        text = (
            f'<text x="28" y="{foot + 70}" font-size="64" letter-spacing="-1.9" fill="{ink}">{name}</text>'
            f'<text x="28" y="{foot + 124}" font-size="44" fill="{sub}">{kind}</text>'
        )
    else:
        note = "".join(f'<tspan x="28" y="{foot + 92 + i * 28}">{t}</tspan>' for i, t in enumerate(line))
        text = (
            f'<text x="28" y="{foot + 52}" font-size="40" letter-spacing="-1.2" fill="{ink}">{name}</text>'
            f'<text font-size="21" fill="{line_ink or ink}">{note}</text>'
            f'<text x="28" y="{foot + 156}" font-size="17" fill="{sub}">{kind}</text>'
        )
    body = (
        f'<rect width="{CW}" height="{h}" rx="4" fill="{bg}"/>{media}'
        f'<rect x="28" y="{foot}" width="{CW - 56}" height="1" fill="{ink}" opacity="0.2"/>{text}'
    )
    return svg(CW + gap, h, label, fonts() + style, body)


def opusbar(small: bool = False) -> str:
    # oneko sheet: 8x4 frames of 32px; the run pose alternates (3,0) and (3,1) every 250ms, as on the site.
    s = 4
    x0, y0 = (CW - 32 * s) / 2, 96 if small else 120
    media = (
        f'<svg x="{x0}" y="{y0}" width="{32 * s}" height="{32 * s}" viewBox="96 0 32 32" overflow="hidden">'
        f'<image class="cat" href="{data_uri("oneko.png", "image/png")}" width="256" height="128" '
        'image-rendering="pixelated" style="image-rendering:pixelated"/></svg>'
    )
    style = "@keyframes run{0%,49.9%{transform:translateY(0)}50%,100%{transform:translateY(-32px)}}.cat{animation:run .5s infinite}"
    return card(
        "OpusBar, a macOS menu bar app: a pixel cat that shows what your Claude Code and Codex sessions are doing.",
        "#F5F1E4", "#2C2E2A", "#5F6159", "OpusBar", "Menu bar app" if small else "macOS menu bar app · 2026",
        media, ("Your Claude Code and Codex", "sessions, in the menu bar."), style=style, small=small,
    )


def athena(small: bool = False) -> str:
    # A crop of the landing page's install terminal: the window bar and the typed npm command.
    iw = CW - 56
    ih = 214 if small else iw * 0.62
    y = 56 if small else 72
    crop_w = 420  # from the terminal's left edge to just past the command
    crop_h = crop_w * ih / iw
    media = (
        '<defs><filter id="shot" x="-20%" y="-20%" width="140%" height="160%">'
        '<feDropShadow dx="0" dy="18" stdDeviation="20" flood-color="#000" flood-opacity="0.5"/></filter></defs>'
        f'<rect x="28" y="{y}" width="{iw}" height="{ih:.1f}" rx="4" fill="#18181B" stroke="#26262B" filter="url(#shot)"/>'
        f'<svg x="28" y="{y}" width="{iw}" height="{ih:.1f}" viewBox="150 176 {crop_w} {crop_h:.1f}" overflow="hidden">'
        f'<image href="{data_uri("athena.webp", "image/webp")}" width="1040" height="646"/></svg>'
    )
    return card(
        "Athena, an open-source AI coding agent for the terminal that knows your codebase, not just your prompt. Screenshot of its install terminal.",
        # Kind line lifted from the site's #6B6B70 muted grey, which is 3.5:1 on #121214, too low for small text.
        "#121214", "#ECE9E4", "#9A9AA0", "Athena", "Coding agent" if small else "Terminal coding agent · 2026",
        media, ("A coding agent that knows", "your codebase."), small=small,
    )


def graphy(small: bool = False) -> str:
    # A crop of the screenshot that reads at card size: the Explorer with Graphy's LineLens line-count badges.
    iw = CW - 56
    ih = 214 if small else iw * 0.62
    y = 56 if small else 72
    crop_w = 300  # the Explorer column only; wider crops cut through the editor pane
    crop_h = crop_w * ih / iw
    media = (
        '<defs><filter id="shot" x="-20%" y="-20%" width="140%" height="160%">'
        '<feDropShadow dx="0" dy="18" stdDeviation="20" flood-color="#000" flood-opacity="0.28"/></filter></defs>'
        f'<rect x="28" y="{y}" width="{iw}" height="{ih:.1f}" rx="4" fill="#181818" filter="url(#shot)"/>'
        f'<svg x="28" y="{y}" width="{iw}" height="{ih:.1f}" viewBox="4 96 {crop_w} {crop_h:.1f}" overflow="hidden">'
        f'<image href="{data_uri("graphy.webp", "image/webp")}" width="1040" height="646"/></svg>'
    )
    return card(
        "Graphy, an editor extension that gives AI coding tools a map of your codebase. Screenshot of LineLens line-count badges in the Explorer.",
        # Kind line in deep navy: white on Graphy blue is 3.35:1, too low for small text.
        # On phones the name renders near 18px, too small for white at 3.35:1, so it takes the navy too.
        "#5A8BE6", "#0F1E3D" if small else "#FFFFFF", "#0F1E3D", "Graphy", "Extension" if small else "Editor extension · 2025",
        media, ("A map of your codebase", "for AI coding tools."), line_ink="#0F1E3D", small=small,
    )


def openticker(small: bool = False) -> str:
    # The landing page's hero, headline and live desk, as the site's own hover preview shows it.
    iw = CW - 56
    ih = 214 if small else iw * 0.62
    y = 56 if small else 72
    media = (
        '<defs><filter id="shot" x="-20%" y="-20%" width="140%" height="160%">'
        '<feDropShadow dx="0" dy="18" stdDeviation="20" flood-color="#000" flood-opacity="0.5"/></filter></defs>'
        f'<rect x="28" y="{y}" width="{iw}" height="{ih:.1f}" rx="4" fill="#0A0A0B" stroke="#1B1B1D" filter="url(#shot)"/>'
        f'<svg x="28" y="{y}" width="{iw}" height="{ih:.1f}" viewBox="0 0 960 600" overflow="hidden">'
        f'<image href="{data_uri("openticker.webp", "image/webp")}" width="960" height="600"/></svg>'
    )
    return card(
        "OpenTicker, coming soon: a self-hosted trading platform your AI agent operates and you control. Screenshot of its landing page.",
        "#050505", "#F5F5F2", "#A6A6A1", "OpenTicker", "Trading platform" if small else "Trading platform · Soon",
        media, ("Self-hosted trading your AI", "agent operates, you control."), small=small,
    )


# ---------- Footer: the page curves into ink ----------
def signature() -> str:
    """The Tegaki "Kushal" strokes from the site; each path draws in order."""
    src = (SRC / "signature.astro").read_text()
    out = ""
    for d, dur, t in re.findall(r'<path d="([^"]+)" style="--d:([\d.]+)s;--t:([\d.]+)s"', src):
        out += (
            f'<path d="{d}" pathLength="1" stroke-dasharray="1" '
            f'style="animation:draw {dur}s {EASE} {float(t) + 0.4:.2f}s both"/>'
        )
    return out


def footer(small: bool = False, dark: bool = False) -> str:
    """Above the curve the image is transparent, so GitHub's own page is the page that curves into the footer.
    On GitHub's light page the curve casts the site's soft shadow; on the dark page a shadow reads as mud,
    so the curve is drawn as a hairline instead."""
    if small:
        w, h, curve_h, line_y, r = 720, 780, 70, 460, 100
    else:
        w, h, curve_h, line_y, r = 1280, 640, 110, 470, 95
    rx = w * 0.75
    edge = curve_h * (1 - ((w / 2) / rx) ** 2) ** 0.5  # where the curve meets the image's sides
    ink = f"M0 {edge:.1f}A{rx} {curve_h} 0 0 0 {w} {edge:.1f}V{h}H0Z"
    curve = f"M0 {edge:.1f}A{rx} {curve_h} 0 0 0 {w} {edge:.1f}"
    m = 48 if small else 80  # side margin
    if dark:
        depth = f'<path d="{curve}" fill="none" stroke="{PAPER}" stroke-opacity="0.18" stroke-width="1.5"/>'
    else:
        depth = (
            f'<g clip-path="url(#panel)"><ellipse cx="{w / 2}" cy="12" rx="{rx}" ry="{curve_h}" fill="#000" '
            'opacity="0.45" filter="url(#edge)"/></g>'
        )
    if small:
        av, head_px = (m, curve_h + 70, 80), 96
        heading = (
            f'<text fill="{PAPER}" font-size="{head_px}" letter-spacing="-2.9"><tspan x="{m + 100}" y="{curve_h + 140}">Let’s work</tspan>'
            f'<tspan x="{m}" y="{curve_h + 240}">together</tspan></text>'
        )
        btn_x, cta_px, meta_px = w - 190, 28, 30
        meta_y = (line_y + 150, line_y + 196)
        sig = f"translate({w - 300} {h - 112}) scale(0.68) translate(-10 -36)"
    else:
        av, head_px = (m, curve_h + 102, 96), 112
        heading = (
            f'<text fill="{PAPER}" font-size="{head_px}" letter-spacing="-3.4"><tspan x="200" y="{curve_h + 192}">Let’s work</tspan>'
            f'<tspan x="{m}" y="{curve_h + 304}">together</tspan></text>'
        )
        btn_x, cta_px, meta_px = w - 420, 22, 24
        meta_y = (line_y + 92, line_y + 130)
        sig = f"translate({w - 300} {line_y + 70}) scale(0.58) translate(-10 -36)"
    ax, ay, asz = av
    body = (
        '<defs><filter id="edge" x="-10%" y="-50%" width="120%" height="300%">'
        '<feGaussianBlur stdDeviation="22"/></filter>'
        f'<clipPath id="panel"><path d="{ink}"/></clipPath>'
        f'<clipPath id="av"><circle cx="{ax + asz / 2}" cy="{ay + asz / 2}" r="{asz / 2}"/></clipPath></defs>'
        f'<path d="{ink}" fill="{INK}"/>{depth}'
        f'<image href="{data_uri("avatar-head.webp", "image/webp")}" x="{ax}" y="{ay}" width="{asz}" height="{asz}" clip-path="url(#av)"/>'
        f'{heading}'
        f'<rect x="{m}" y="{line_y}" width="{w - 2 * m}" height="1" fill="{PAPER}" opacity="0.2"/>'
        f'<circle cx="{btn_x}" cy="{line_y}" r="{r}" fill="{BLUE}"/>'
        f'<text x="{btn_x}" y="{line_y}" font-size="{cta_px}" fill="{PAPER}" text-anchor="middle" dominant-baseline="middle">Get in touch</text>'
        f'<text x="{m}" y="{meta_y[0]}" font-size="{meta_px}" fill="#A3A5AA">kushalbanda265@gmail.com</text>'
        f'<text x="{m}" y="{meta_y[1]}" font-size="{meta_px}" fill="#A3A5AA">kushalbanda.com</text>'
        f'<g transform="{sig}" fill="none" stroke="{PAPER}" '
        f'stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round">{signature()}</g>'
    )
    style = fonts() + "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
    return svg(w, h, "Let’s work together. Get in touch: kushalbanda265@gmail.com", style, body)


if __name__ == "__main__":
    for small in (False, True):
        sm = "-sm" if small else ""
        write(f"header{sm}.svg", header(small))
        write(f"opusbar{sm}.svg", opusbar(small))
        write(f"athena{sm}.svg", athena(small))
        write(f"graphy{sm}.svg", graphy(small))
        write(f"openticker{sm}.svg", openticker(small))
        write(f"footer{sm}.svg", footer(small))
        write(f"footer{sm}-dark.svg", footer(small, dark=True))
