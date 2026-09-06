"""Live system monitor: what the account actually looks like right now.

Language allocation, headline counters and the most recent pushes, all measured
from the GitHub API at build time instead of borrowed from a stats service.
"""

from .common import (
    BG, CYAN, GREEN, MONO, MUTED, PANEL, PANEL_EDGE, RED, RED_DIM, TEXT,
    corner_brackets, defs_common, document, esc, grid, readable,
)

W, H = 1200, 430

# Language accents, roughly GitHub's own linguist colours.
LANG_COLORS = {
    "TypeScript": "#3178C6", "JavaScript": "#F1E05A", "Python": "#3572A5",
    "HTML": "#E34C26", "CSS": "#563D7C", "Lua": "#000080", "Go": "#00ADD8",
    "Shell": "#89E051", "Java": "#B07219", "C#": "#178600", "PHP": "#4F5D95",
    "Ruby": "#701516", "Rust": "#DEA584", "C++": "#F34B7D", "Dart": "#00B4AB",
    "Vue": "#41B883", "Svelte": "#FF3E00", "SCSS": "#C6538C", "Kotlin": "#A97BFF",
}
FALLBACK_COLORS = (RED, CYAN, "#F778BA", "#A371F7", "#3FB950", "#D29922")


def _lang_color(name, index):
    return readable(LANG_COLORS.get(name, FALLBACK_COLORS[index % len(FALLBACK_COLORS)]))


def _panel(x, y, w, h, label):
    return f"""<g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{PANEL}"
          stroke="{PANEL_EDGE}"/>
    <rect x="{x}" y="{y}" width="{w}" height="2" fill="url(#edgeGrad)"/>
    <text x="{x + 16}" y="{y + 26}" font-family="{MONO}" font-size="11"
          letter-spacing="3" fill="{MUTED}">{esc(label)}</text>
  </g>"""


def _bars(langs, x, y, width):
    """Horizontal allocation bars that grow once, on load, then hold."""
    rows = []
    for i, (name, share) in enumerate(langs):
        top = y + i * 42
        color = _lang_color(name, i)
        fill_w = max(4, round(width * share))
        rows.append(f"""<g>
      <text x="{x}" y="{top}" font-family="{MONO}" font-size="13" fill="{TEXT}">{esc(name)}</text>
      <text x="{x + width}" y="{top}" font-family="{MONO}" font-size="12"
            fill="{color}" text-anchor="end">{share * 100:.1f}%</text>
      <rect x="{x}" y="{top + 8}" width="{width}" height="7" rx="3.5" fill="#12161F"/>
      <rect x="{x}" y="{top + 8}" width="0" height="7" rx="3.5" fill="{color}" opacity="0.92">
        <animate attributeName="width" values="0;{fill_w}" dur="1.1s"
                 begin="{i * 0.13:.2f}s" fill="freeze" calcMode="spline"
                 keySplines="0.2 0.8 0.2 1"/>
      </rect>
      <rect x="{x}" y="{top + 8}" width="0" height="7" rx="3.5" fill="#FFFFFF" opacity="0.16">
        <animate attributeName="width" values="0;{fill_w}" dur="1.1s"
                 begin="{i * 0.13:.2f}s" fill="freeze"/>
        <animate attributeName="opacity" values="0.20;0.03;0.20" dur="3.4s"
                 begin="{i * 0.13:.2f}s" repeatCount="indefinite"/>
      </rect>
    </g>""")
    return "".join(rows)


def _tile(x, y, w, label, value, accent):
    return f"""<g>
    <rect x="{x}" y="{y}" width="{w}" height="72" rx="3" fill="#0D1018" stroke="{PANEL_EDGE}"/>
    <rect x="{x}" y="{y}" width="3" height="72" fill="{accent}"/>
    <text x="{x + 14}" y="{y + 26}" font-family="{MONO}" font-size="10"
          letter-spacing="1.2" fill="{MUTED}">{esc(label)}</text>
    <text x="{x + 14}" y="{y + 56}" font-family="{MONO}" font-size="26"
          font-weight="700" fill="{accent}">{esc(value)}</text>
  </g>"""


def _pushes(items, x, y, width):
    rows = []
    for i, (name, lang, when) in enumerate(items):
        top = y + i * 26
        color = _lang_color(lang, i) if lang else MUTED
        name = name if len(name) <= 26 else name[:25] + "…"
        rows.append(f"""<g opacity="0">
      <circle cx="{x + 4}" cy="{top - 4}" r="3.5" fill="{color}"/>
      <text x="{x + 18}" y="{top}" font-family="{MONO}" font-size="12.5" fill="{TEXT}">{esc(name)}</text>
      <text x="{x + width}" y="{top}" font-family="{MONO}" font-size="12"
            fill="{MUTED}" text-anchor="end">{esc(when)}</text>
      <animate attributeName="opacity" values="0;1" dur="0.4s"
               begin="{0.5 + i * 0.12:.2f}s" fill="freeze"/>
    </g>""")
    return "".join(rows)


def render(data):
    langs = data["languages"][:6]
    left_w, right_x = 590, 664
    right_w = W - right_x - 40
    tile_w = (right_w - 32 - 3 * 12) / 4

    tiles = "".join(
        _tile(right_x + 16 + i * (tile_w + 12), 106, tile_w, label, value, accent)
        for i, (label, value, accent) in enumerate((
            ("REPOSITORIES", str(data["repos"]), RED),
            ("FOLLOWERS", str(data["followers"]), CYAN),
            ("STARS EARNED", str(data["stars"]), RED),
            ("YEARS ACTIVE", data["years"], CYAN),
        ))
    )

    body = f"""{defs_common(W, H)}
<rect width="{W}" height="{H}" fill="{BG}"/>
{grid(W, H, 40, RED, 0.04)}
<ellipse cx="240" cy="200" rx="420" ry="260" fill="url(#glowRed)" opacity="0.5"/>

<text x="40" y="42" font-family="{MONO}" font-size="13" letter-spacing="4"
      fill="{TEXT}">ITALO//OS  ·  SYSTEM MONITOR</text>
<g>
  <circle cx="{W - 208}" cy="37" r="4" fill="{GREEN}">
    <animate attributeName="opacity" values="1;0.15;1" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <text x="{W - 194}" y="42" font-family="{MONO}" font-size="11" letter-spacing="1.5"
        fill="{MUTED}">SYNCED {esc(data['synced'])}</text>
</g>
<line x1="40" y1="56" x2="{W - 40}" y2="56" stroke="{PANEL_EDGE}"/>

{_panel(40, 72, left_w, 330, 'LANGUAGE ALLOCATION')}
{_bars(langs, 56, 128, left_w - 32)}

{_panel(right_x, 72, right_w, 124, 'VITALS')}
{tiles}

{_panel(right_x, 210, right_w, 192, 'RECENT PUSHES')}
{_pushes(data['recent'], right_x + 16, 264, right_w - 32)}

<text x="40" y="{H - 14}" font-family="{MONO}" font-size="10" letter-spacing="1.5"
      fill="{MUTED}">rendered by scripts/build.py · no third-party stats service</text>
{corner_brackets(W, H, 20, 12, RED, 0.5)}
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" stroke="{RED}" stroke-opacity="0.28" fill="none"/>"""

    return document(W, H, body, "Live system monitor for the italodevjs account")
