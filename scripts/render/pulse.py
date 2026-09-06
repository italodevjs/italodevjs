"""Contribution history drawn as a cardiogram.

A year of commits becomes an ECG trace: flat where the year went quiet, spiking
where it did not. Fed by the GraphQL contribution calendar, redrawn nightly.
"""

import math

from .common import (
    BG, CYAN, MONO, MUTED, PANEL_EDGE, RED, RED_DIM, TEXT,
    corner_brackets, defs_common, document, esc, grid,
)

W, H = 1200, 380
PAD_X = 58
BASELINE = 268
AMPLITUDE = 130
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def _scale(days):
    """The busiest day sets the top of the axis."""
    return max(1, max((c for _, c in days), default=1))


def _norm(count, ceiling):
    """Log scale, because this history spans three orders of magnitude.

    A typical active day here sits near single digits while automated days run
    into the thousands. Linear scaling would render everything but the peaks as
    a flat line, hiding most of the actual work; a log axis keeps both regimes
    legible in the same trace.
    """
    return math.log1p(count) / math.log1p(ceiling)


def _trace(days, ceiling):
    """Build the ECG polyline: baseline between days, a spike on each active one."""
    if not days:
        return "", []
    step = (W - PAD_X * 2) / max(1, len(days) - 1)
    points, peaks = [], []
    for i, (_, count) in enumerate(days):
        x = PAD_X + i * step
        if count <= 0:
            points.append((x, BASELINE))
            continue
        height = min(1.0, _norm(count, ceiling)) * AMPLITUDE
        points.append((x, BASELINE))
        points.append((x + step * 0.25, BASELINE - height))
        points.append((x + step * 0.5, BASELINE + min(14, height * 0.18)))
        points.append((x + step * 0.75, BASELINE))
        if height > AMPLITUDE * 0.72:
            peaks.append((x + step * 0.25, BASELINE - height, count))
    path = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points)
    return path, peaks


def _month_axis(days):
    if not days:
        return ""
    step = (W - PAD_X * 2) / max(1, len(days) - 1)
    marks, seen = [], set()
    for i, (date, _) in enumerate(days):
        month = date[:7]
        if month in seen:
            continue
        seen.add(month)
        x = PAD_X + i * step
        if x > W - PAD_X - 46:
            continue
        label = MONTHS[int(date[5:7]) - 1]
        marks.append(
            f'<line x1="{x:.1f}" y1="296" x2="{x:.1f}" y2="304" stroke="{PANEL_EDGE}"/>'
            f'<text x="{x:.1f}" y="330" font-family="{MONO}" font-size="17" '
            f'letter-spacing="1.5" fill="{MUTED}">{label}</text>'
        )
    return "".join(marks)


def _readout(label, value, x, accent=RED):
    return f"""<g transform="translate({x} 0)">
    <text x="0" y="50" font-family="{MONO}" font-size="17" letter-spacing="2" fill="{MUTED}">{esc(label)}</text>
    <text x="0" y="92" font-family="{MONO}" font-size="38" font-weight="700" fill="{accent}">{esc(value)}</text>
  </g>"""


def render(days, stats):
    """days: [(YYYY-MM-DD, count)] oldest first. stats: dict of headline numbers."""
    ceiling = _scale(days)
    path, peaks = _trace(days, ceiling)
    awaiting = "" if days else (
        f'<text x="{W // 2}" y="{BASELINE - 30}" font-family="{MONO}" font-size="20" '
        f'letter-spacing="3" fill="{MUTED}" text-anchor="middle">'
        f'AWAITING FIRST SYNC — the nightly build fills this in'
        f'<animate attributeName="opacity" values="0.35;1;0.35" dur="2.4s" '
        f'repeatCount="indefinite"/></text>'
    )

    peak_marks = "".join(
        f'<g opacity="0.9"><circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{CYAN}"/>'
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="none" stroke="{CYAN}" stroke-width="1">'
        f'<animate attributeName="r" values="3;11;3" dur="2.6s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.9;0;0.9" dur="2.6s" repeatCount="indefinite"/>'
        f"</circle></g>"
        for x, y, _ in peaks[:14]
    )

    area = f"{path} L{W - PAD_X} {BASELINE} L{PAD_X} {BASELINE} Z" if path else ""

    body = f"""{defs_common(W, H)}
<defs>
  <linearGradient id="ecgArea" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{RED}" stop-opacity="0.38"/>
    <stop offset="100%" stop-color="{RED}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="ecgStroke" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{RED_DIM}"/>
    <stop offset="45%" stop-color="{RED}"/>
    <stop offset="100%" stop-color="{CYAN}"/>
  </linearGradient>
  <linearGradient id="probeGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0.75"/>
  </linearGradient>
  <clipPath id="ecgReveal">
    <rect x="0" y="0" width="0" height="{H}">
      <animate attributeName="width" values="0;{W}" dur="4.5s" fill="freeze"/>
    </rect>
  </clipPath>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
{grid(W, H, 30, RED, 0.045)}
<ellipse cx="600" cy="{BASELINE}" rx="620" ry="180" fill="url(#glowRed)" opacity="0.35"/>

<text x="{PAD_X}" y="50" font-family="{MONO}" font-size="22" letter-spacing="4"
      fill="{TEXT}">CONTRIBUTION CARDIOGRAM</text>
<text x="{PAD_X}" y="80" font-family="{MONO}" font-size="17" letter-spacing="1.5"
      fill="{MUTED}">last 365 days · log scale</text>

<g transform="translate({W - 620} 0)">
  {_readout('TOTAL', stats.get('total', '—'), 0)}
  {_readout('PEAK DAY', stats.get('peak', '—'), 170, CYAN)}
  {_readout('LONGEST', stats.get('longest', '—'), 340)}
  {_readout('CURRENT', stats.get('current', '—'), 480, CYAN)}
</g>

<line x1="{PAD_X}" y1="{BASELINE}" x2="{W - PAD_X}" y2="{BASELINE}"
      stroke="{PANEL_EDGE}" stroke-dasharray="3 6"/>

<g clip-path="url(#ecgReveal)">
  <path d="{area}" fill="url(#ecgArea)"/>
  <path d="{path}" fill="none" stroke="url(#ecgStroke)" stroke-width="1.9"
        stroke-linejoin="round" stroke-linecap="round" filter="url(#softGlow)"/>
  {peak_marks}
</g>

<g opacity="0.55">
  <rect x="0" y="110" width="70" height="190" fill="url(#probeGrad)"/>
  <rect x="68" y="110" width="2" height="190" fill="{CYAN}"/>
  <animateTransform attributeName="transform" type="translate"
                    values="0 0;{W - 70} 0" dur="4.5s" fill="freeze"/>
  <animate attributeName="opacity" values="0.55;0.55;0" keyTimes="0;0.82;1"
           dur="4.5s" fill="freeze"/>
</g>

{awaiting}
{_month_axis(days)}
{corner_brackets(W, H, 22, 12, RED, 0.55)}
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" stroke="{RED}" stroke-opacity="0.28" fill="none"/>"""

    return document(W, H, body, "Contribution cardiogram for the last 365 days")
