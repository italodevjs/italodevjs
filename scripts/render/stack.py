"""Capability radar plus the actual toolchain, drawn from scratch.

No icon CDN: every mark here is a primitive in this file, so the panel keeps
working even if half the internet goes down.
"""

import math

from .common import (
    BG, CYAN, MONO, MUTED, PANEL_EDGE, RED, RED_DIM, TEXT,
    corner_brackets, defs_common, document, esc, grid,
)

W, H = 1200, 430
CX, CY, R = 268, 244, 126

AXES = (
    ("FRONT-END", 0.92),
    ("BACK-END", 0.88),
    ("SECURITY", 0.95),
    ("DEVOPS", 0.78),
    ("DATA", 0.74),
    ("AUTOMATION", 0.85),
)

STACK = (
    ("INTERFACE", CYAN, ("React", "Next.js", "TypeScript", "Tailwind", "Vite")),
    ("SERVICES", RED, ("Node.js", "NestJS", "Python", "Prisma", "REST / GraphQL")),
    ("DATA", "#A371F7", ("PostgreSQL", "MongoDB", "Redis", "Supabase")),
    ("PLATFORM", "#3FB950", ("Docker", "Linux", "Nginx", "GitHub Actions")),
    ("OFFENSIVE", "#F778BA", ("OWASP Top 10", "Burp Suite", "Nmap", "Threat modelling")),
    ("DEFENSIVE", "#D29922", ("Secure code review", "Hardening", "Zero-trust", "IR playbooks")),
)


def _point(index, radius):
    angle = math.radians(-90 + index * (360 / len(AXES)))
    return CX + radius * math.cos(angle), CY + radius * math.sin(angle)


def _polygon(radii):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in
                    (_point(i, r) for i, r in enumerate(radii)))


def _web():
    rings = []
    for ratio in (0.25, 0.5, 0.75, 1.0):
        pts = _polygon([R * ratio] * len(AXES))
        rings.append(
            f'<polygon points="{pts}" fill="none" stroke="{PANEL_EDGE}" '
            f'stroke-width="1" opacity="{0.9 if ratio == 1.0 else 0.55}"/>'
        )
    for i in range(len(AXES)):
        x, y = _point(i, R)
        rings.append(
            f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" '
            f'stroke="{PANEL_EDGE}" stroke-width="1" opacity="0.7"/>'
        )
    return "".join(rings)


def _labels():
    out = []
    for i, (name, value) in enumerate(AXES):
        x, y = _point(i, R + 34)
        if abs(x - CX) < 12:
            anchor = "middle"
        elif x > CX:
            anchor = "start"
        else:
            anchor = "end"
        out.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="11" '
            f'letter-spacing="1.6" fill="{TEXT}" text-anchor="{anchor}">{esc(name)}</text>'
            f'<text x="{x:.1f}" y="{y + 15:.1f}" font-family="{MONO}" font-size="10" '
            f'fill="{RED}" text-anchor="{anchor}">{int(value * 100)}</text>'
        )
    return "".join(out)


def _vertices(radii):
    out = []
    for i, radius in enumerate(radii):
        x, y = _point(i, radius)
        out.append(f"""<g opacity="0">
      <circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{RED}"/>
      <circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="none" stroke="{RED}" stroke-width="1">
        <animate attributeName="r" values="3.5;12;3.5" dur="3s"
                 begin="{i * 0.4:.1f}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.8;0;0.8" dur="3s"
                 begin="{i * 0.4:.1f}s" repeatCount="indefinite"/>
      </circle>
      <animate attributeName="opacity" values="0;1" dur="0.4s" begin="1.2s" fill="freeze"/>
    </g>""")
    return "".join(out)


def _columns():
    out = []
    col_w, x0, y0 = 186, 608, 112
    for i, (title, accent, items) in enumerate(STACK):
        x = x0 + (i % 3) * col_w
        y = y0 + (i // 3) * 140
        rows = "".join(
            f'<rect x="{x}" y="{y + 18 + j * 19}" width="6" height="6" fill="{accent}" opacity="0.85"/>'
            f'<text x="{x + 14}" y="{y + 24 + j * 19}" font-family="{MONO}" font-size="12" '
            f'fill="{MUTED}">{esc(item)}</text>'
            for j, item in enumerate(items)
        )
        out.append(f"""<g opacity="0">
      <text x="{x}" y="{y}" font-family="{MONO}" font-size="11" letter-spacing="2.4"
            fill="{accent}">{esc(title)}</text>
      <line x1="{x}" y1="{y + 7}" x2="{x + col_w - 26}" y2="{y + 7}" stroke="{PANEL_EDGE}"/>
      {rows}
      <animate attributeName="opacity" values="0;1" dur="0.5s" begin="{0.3 + i * 0.13:.2f}s" fill="freeze"/>
    </g>""")
    return "".join(out)


def render():
    radii = [R * value for _, value in AXES]
    collapsed = _polygon([2.0] * len(AXES))
    target = _polygon(radii)

    body = f"""{defs_common(W, H)}
<defs>
  <radialGradient id="radarFill" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{RED}" stop-opacity="0.42"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0.14"/>
  </radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
{grid(W, H, 40, RED, 0.04)}
<ellipse cx="{CX}" cy="{CY}" rx="300" ry="240" fill="url(#glowRed)" opacity="0.55"/>

<text x="40" y="42" font-family="{MONO}" font-size="13" letter-spacing="4"
      fill="{TEXT}">CAPABILITY RADAR  ·  TOOLCHAIN</text>
<text x="40" y="62" font-family="{MONO}" font-size="11" letter-spacing="1.4"
      fill="{MUTED}">self-assessed depth per discipline, and what it is built with</text>
<line x1="40" y1="76" x2="{W - 40}" y2="76" stroke="{PANEL_EDGE}"/>

{_web()}
<polygon points="{collapsed}" fill="url(#radarFill)" stroke="{RED}" stroke-width="2"
         stroke-linejoin="round" filter="url(#softGlow)">
  <animate attributeName="points" values="{collapsed};{target}" dur="1.3s"
           begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
</polygon>
{_vertices(radii)}
{_labels()}
<circle cx="{CX}" cy="{CY}" r="3" fill="{RED_DIM}"/>

{_columns()}
{corner_brackets(W, H, 20, 12, RED, 0.5)}
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" stroke="{RED}" stroke-opacity="0.28" fill="none"/>"""

    return document(W, H, body, "Capability radar and toolchain")
