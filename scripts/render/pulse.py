"""Contribution history drawn as a cardiogram.

A year of commits becomes an ECG trace: flat where the year went quiet, spiking
where it did not. Fed by the GraphQL contribution calendar, redrawn nightly.
"""

from .common import (
    BG, CYAN, MONO, MUTED, PANEL_EDGE, RED, RED_DIM, TEXT,
    corner_brackets, defs_common, document, esc, grid,
)

W, H = 1200, 300
PAD_X = 58
BASELINE = 208
AMPLITUDE = 118
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def _scale(days):
    """Cap the axis at the 95th percentile so one huge day can't flatten the rest."""
    counts = sorted(c for _, c in days if c > 0)
    if not counts:
        return 1
    ceiling = counts[int(len(counts) * 0.95) - 1] if len(counts) > 4 else counts[-1]
    return max(1, ceiling)


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
        height = min(1.0, count / ceiling) * AMPLITUDE
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
        if x > W - PAD_X - 30:
            continue
        label = MONTHS[int(date[5:7]) - 1]
        marks.append(
            f'<line x1="{x:.1f}" y1="236" x2="{x:.1f}" y2="242" stroke="{PANEL_EDGE}"/>'
            f'<text x="{x:.1f}" y="256" font-family="{MONO}" font-size="10" '
            f'letter-spacing="1.5" fill="{MUTED}">{label}</text>'
        )
    return "".join(marks)


def _readout(label, value, x, accent=RED):
    return f"""<g transform="translate({x} 0)">
    <text x="0" y="52" font-family="{MONO}" font-size="10" letter-spacing="2" fill="{MUTED}">{esc(label)}</text>
    <text x="0" y="76" font-family="{MONO}" font-size="22" font-weight="700" fill="{accent}">{esc(value)}</text>
  </g>"""


def render(days, stats):
    """days: [(YYYY-MM-DD, count)] oldest first. stats: dict of headline numbers."""
    ceiling = _scale(days)
    path, peaks = _trace(days, ceiling)
    awaiting = "" if days else (
        f'<text x="{W // 2}" y="{BASELINE - 24}" font-family="{MONO}" font-size="13" '
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

<text x="{PAD_X}" y="46" font-family="{MONO}" font-size="14" letter-spacing="4"
      fill="{TEXT}">CONTRIBUTION CARDIOGRAM</text>
<text x="{PAD_X}" y="66" font-family="{MONO}" font-size="11" letter-spacing="1.5"
      fill="{MUTED}">last 365 days · sampled from the commit stream</text>

<g transform="translate({W - 470} 0)">
  {_readout('TOTAL', stats.get('total', '—'), 0)}
  {_readout('PEAK DAY', stats.get('peak', '—'), 130, CYAN)}
  {_readout('LONGEST', stats.get('longest', '—'), 260)}
  {_readout('CURRENT', stats.get('current', '—'), 370, CYAN)}
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
  <rect x="0" y="70" width="70" height="160" fill="url(#probeGrad)"/>
  <rect x="68" y="70" width="2" height="160" fill="{CYAN}"/>
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
