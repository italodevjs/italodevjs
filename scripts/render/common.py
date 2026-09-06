"""Shared palette, font stack and SVG primitives for the ITALO//OS README build.

Everything here emits plain SVG strings. No runtime deps, no third-party
services: GitHub renders these files as static images, so animation has to be
SMIL/CSS living inside the document itself.
"""

BG = "#05060A"
PANEL = "#0A0C12"
PANEL_EDGE = "#161B26"
RED = "#FF0033"
RED_DIM = "#8B0000"
CYAN = "#00E5FF"
TEXT = "#E6EDF3"
MUTED = "#6E7681"
GREEN = "#3FB950"

MONO = "ui-monospace,'SF Mono','Cascadia Code','Fira Code',Menlo,Consolas,'DejaVu Sans Mono',monospace"

XML_ESCAPES = (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;"))


def esc(value):
    text = str(value)
    for raw, encoded in XML_ESCAPES:
        text = text.replace(raw, encoded)
    return text


def keyframes(total, stops):
    """Turn absolute seconds into the keyTimes fraction list SMIL wants."""
    return ";".join(f"{max(0.0, min(1.0, s / total)):.5f}" for s in stops)


def typewriter(clip_id, x, y, width, height, start, duration, total):
    """A clip path whose rect widens on cue, revealing text character by character.

    The reveal snaps shut just before the loop restarts so the animation never
    plays backwards.
    """
    stops = [0, start, start + duration, total * 0.985, total * 0.99, total]
    values = f"0;0;{width};{width};0;0"
    return (
        f'<clipPath id="{clip_id}">'
        f'<rect x="{x}" y="{y}" width="0" height="{height}">'
        f'<animate attributeName="width" values="{values}" '
        f'keyTimes="{keyframes(total, stops)}" dur="{total}s" '
        f'calcMode="linear" repeatCount="indefinite"/>'
        f"</rect></clipPath>"
    )


def fade_in(start, duration, total, hold_to=None):
    """An <animate> that fades an element in on cue and holds it for the loop."""
    end = total * 0.985 if hold_to is None else hold_to
    stops = [0, start, start + duration, end, total * 0.995, total]
    return (
        f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
        f'keyTimes="{keyframes(total, stops)}" dur="{total}s" '
        f'calcMode="linear" repeatCount="indefinite"/>'
    )


def grid(width, height, step=40, color=RED, opacity=0.055):
    """Faint engineering grid — the substrate every panel sits on."""
    parts = []
    for x in range(0, width + 1, step):
        parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}"/>')
    for y in range(0, height + 1, step):
        parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}"/>')
    return (
        f'<g stroke="{color}" stroke-width="1" opacity="{opacity}">'
        + "".join(parts)
        + "</g>"
    )


def scanline(width, height, duration=6.0, band=90, opacity=0.5):
    """CRT sweep travelling top to bottom, forever."""
    return f"""<g opacity="{opacity}">
  <rect x="0" y="0" width="{width}" height="{band}" fill="url(#sweepGrad)">
    <animate attributeName="y" values="{-band};{height}" dur="{duration}s" repeatCount="indefinite"/>
  </rect>
</g>"""


def corner_brackets(width, height, size=22, inset=10, color=RED, opacity=0.85):
    """Four HUD corner marks that frame the panel."""
    x0, y0 = inset, inset
    x1, y1 = width - inset, height - inset
    d = (
        f"M{x0} {y0 + size} L{x0} {y0} L{x0 + size} {y0} "
        f"M{x1 - size} {y0} L{x1} {y0} L{x1} {y0 + size} "
        f"M{x1} {y1 - size} L{x1} {y1} L{x1 - size} {y1} "
        f"M{x0 + size} {y1} L{x0} {y1} L{x0} {y1 - size}"
    )
    return (
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2" '
        f'opacity="{opacity}"/>'
    )


def defs_common(width, height):
    """Gradients and filters reused by every panel in the set."""
    return f"""<defs>
  <linearGradient id="sweepGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{RED}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{RED}" stop-opacity="0.10"/>
    <stop offset="100%" stop-color="{RED}" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="glowRed" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{RED}" stop-opacity="0.30"/>
    <stop offset="100%" stop-color="{RED}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="edgeGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{RED}" stop-opacity="0.9"/>
    <stop offset="60%" stop-color="{RED}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0.35"/>
  </linearGradient>
  <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="hardGlow" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>"""


def document(width, height, body, title):
    """Wrap a body in a root <svg> with the accessibility title GitHub reads."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" aria-label="{esc(title)}" fill="none">'
        f"<title>{esc(title)}</title>"
        f"{body}</svg>\n"
    )


def readable(hex_color, floor=0.42):
    """Lift a colour until it reads against the near-black background.

    Some linguist colours (Lua's navy, Ruby's maroon) vanish on this palette;
    this keeps their hue while raising luminance to a legible floor.
    """
    value = hex_color.lstrip("#")
    r, g, b = (int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if luma >= floor:
        return hex_color
    lift = (floor - luma) / max(1e-6, 1 - luma)
    r, g, b = (channel + (1 - channel) * lift for channel in (r, g, b))
    return "#" + "".join(f"{round(channel * 255):02X}" for channel in (r, g, b))
