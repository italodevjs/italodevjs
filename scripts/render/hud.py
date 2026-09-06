"""Live system monitor: what the account actually looks like right now.

Language allocation, headline counters and the most recent pushes, all measured
from the GitHub API at build time instead of borrowed from a stats service.

Sized for a phone first. GitHub scales a 1200-unit panel down to roughly a
third on a handset, so nothing here is smaller than 16 units and the panel
carries less at once than it comfortably could on a desktop.
"""

from .common import (
    BG, CYAN, GREEN, MONO, MUTED, PANEL, PANEL_EDGE, RED, TEXT,
    corner_brackets, defs_common, document, esc, grid, readable,
)

W, H = 1200, 560

# Language accents, roughly GitHub's own linguist colours.
LANG_COLORS = {
    "TypeScript": "#3178C6", "JavaScript": "#F1E05A", "Python": "#3572A5",
    "HTML": "#E34C26", "CSS": "#563D7C", "Lua": "#000080", "Luau": "#00A2FF",
    "Go": "#00ADD8", "Shell": "#89E051", "Java": "#B07219", "C#": "#178600",
    "PHP": "#4F5D95", "Ruby": "#701516", "Rust": "#DEA584", "C++": "#F34B7D",
    "Dart": "#00B4AB", "Vue": "#41B883", "Svelte": "#FF3E00", "SCSS": "#C6538C",
    "Kotlin": "#A97BFF",
}
FALLBACK_COLORS = (RED, CYAN, "#F778BA", "#A371F7", "#3FB950", "#D29922")


def _lang_color(name, index):
    return readable(LANG_COLORS.get(name, FALLBACK_COLORS[index % len(FALLBACK_COLORS)]))


def _panel(x, y, w, h, label):
    return f"""<g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{PANEL}"
          stroke="{PANEL_EDGE}"/>
    <rect x="{x}" y="{y}" width="{w}" height="2" fill="url(#edgeGrad)"/>
    <text x="{x + 22}" y="{y + 38}" font-family="{MONO}" font-size="17"
          letter-spacing="3" fill="{MUTED}">{esc(label)}</text>
  </g>"""


def _bars(langs, x, y, width):
    """Horizontal allocation bars that grow once, on load, then hold."""
    rows = []
    for i, (name, share) in enumerate(langs):
        top = y + i * 76
        color = _lang_color(name, i)
        fill_w = max(6, round(width * share))
        rows.append(f"""<g>
      <text x="{x}" y="{top}" font-family="{MONO}" font-size="23" fill="{TEXT}">{esc(name)}</text>
      <text x="{x + width}" y="{top}" font-family="{MONO}" font-size="21"
            fill="{color}" text-anchor="end">{share * 100:.0f}%</text>
      <rect x="{x}" y="{top + 14}" width="{width}" height="12" rx="6" fill="#12161F"/>
      <rect x="{x}" y="{top + 14}" width="0" height="12" rx="6" fill="{color}" opacity="0.92">
        <animate attributeName="width" values="0;{fill_w}" dur="1.1s"
                 begin="{i * 0.13:.2f}s" fill="freeze" calcMode="spline"
                 keySplines="0.2 0.8 0.2 1"/>
      </rect>
      <rect x="{x}" y="{top + 14}" width="0" height="12" rx="6" fill="#FFFFFF" opacity="0.16">
        <animate attributeName="width" values="0;{fill_w}" dur="1.1s"
                 begin="{i * 0.13:.2f}s" fill="freeze"/>
        <animate attributeName="opacity" values="0.20;0.03;0.20" dur="3.4s"
                 begin="{i * 0.13:.2f}s" repeatCount="indefinite"/>
      </rect>
    </g>""")
    return "".join(rows)


def _tile(x, y, w, h, label, value, accent):
    return f"""<g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#0D1018" stroke="{PANEL_EDGE}"/>
    <rect x="{x}" y="{y}" width="4" height="{h}" fill="{accent}"/>
    <text x="{x + 20}" y="{y + 34}" font-family="{MONO}" font-size="17"
          letter-spacing="1.4" fill="{MUTED}">{esc(label)}</text>
    <text x="{x + 20}" y="{y + 84}" font-family="{MONO}" font-size="46"
          font-weight="700" fill="{accent}">{esc(value)}</text>
  </g>"""


def _pushes(items, x, y, width):
    rows = []
    for i, (name, lang, when) in enumerate(items):
        top = y + i * 48
        color = _lang_color(lang, i) if lang else MUTED
        name = name if len(name) <= 22 else name[:21] + "…"
        rows.append(f"""<g opacity="0">
      <circle cx="{x + 7}" cy="{top - 7}" r="6" fill="{color}"/>
      <text x="{x + 28}" y="{top}" font-family="{MONO}" font-size="22" fill="{TEXT}">{esc(name)}</text>
      <text x="{x + width}" y="{top}" font-family="{MONO}" font-size="19"
            fill="{MUTED}" text-anchor="end">{esc(when)}</text>
      <animate attributeName="opacity" values="0;1" dur="0.4s"
               begin="{0.5 + i * 0.12:.2f}s" fill="freeze"/>
    </g>""")
    return "".join(rows)


def render(data):
    langs = data["languages"][:5]
    left_x, left_w = 40, 560
    right_x = 640
    right_w = W - right_x - 40

    tile_w = (right_w - 44 - 16) / 2
    tile_h = 104
    tiles = "".join(
        _tile(right_x + 22 + (i % 2) * (tile_w + 16),
              102 + (i // 2) * (tile_h + 16),
              tile_w, tile_h, label, value, accent)
        for i, (label, value, accent) in enumerate((
            ("REPOSITORIES", str(data["repos"]), RED),
            ("FOLLOWERS", str(data["followers"]), CYAN),
            ("STARS", str(data["stars"]), RED),
            ("YEARS", data["years"], CYAN),
        ))
    )

    body = f"""{defs_common(W, H)}
<rect width="{W}" height="{H}" fill="{BG}"/>
{grid(W, H, 40, RED, 0.04)}
<ellipse cx="240" cy="280" rx="460" ry="320" fill="url(#glowRed)" opacity="0.5"/>

<text x="40" y="52" font-family="{MONO}" font-size="21" letter-spacing="4"
      fill="{TEXT}">ITALO//OS  ·  SYSTEM MONITOR</text>
<g>
  <circle cx="{W - 374}" cy="45" r="6" fill="{GREEN}">
    <animate attributeName="opacity" values="1;0.15;1" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <text x="{W - 356}" y="52" font-family="{MONO}" font-size="17" letter-spacing="1.2"
        fill="{MUTED}">SYNCED {esc(data['synced'])}</text>
</g>
<line x1="40" y1="70" x2="{W - 40}" y2="70" stroke="{PANEL_EDGE}"/>

{_panel(left_x, 88, left_w, 432, 'LANGUAGE ALLOCATION')}
{_bars(langs, left_x + 22, 156, left_w - 44)}

{_panel(right_x, 88, right_w, 252, 'VITALS')}
{tiles}

{_panel(right_x, 356, right_w, 164, 'RECENT PUSHES')}
{_pushes(data['recent'][:3], right_x + 22, 424, right_w - 44)}

<text x="40" y="{H - 18}" font-family="{MONO}" font-size="15" letter-spacing="1.2"
      fill="{MUTED}">rendered by scripts/build.py · no third-party stats service</text>
{corner_brackets(W, H, 24, 12, RED, 0.5)}
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" stroke="{RED}" stroke-opacity="0.28" fill="none"/>"""

    return document(W, H, body, "Live system monitor for the italodevjs account")
