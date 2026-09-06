"""The masthead: a glitching identity plate with a live boot sequence.

Hand-authored SVG, no external service. The whole thing runs on one 12 second
SMIL timeline so every element loops in sync.
"""

from .common import (
    BG, CYAN, MONO, MUTED, RED, RED_DIM, TEXT,
    corner_brackets, defs_common, document, esc, fade_in, grid, keyframes,
    scanline, typewriter,
)

W, H = 1200, 470
LOOP = 12.0

TITLE = "ITALODEVJS"
SUBTITLE = "FULL-STACK ENGINEER  //  SECURITY ENGINEERING"

BOOT = [
    ("ok", "kernel", "loaded"),
    ("ok", "/skills/fullstack", "mounted"),
    ("ok", "/skills/appsec", "armed"),
    ("ok", "secure channel", "aes-256-gcm"),
    (">>", "identity", "italodevjs @ br"),
]

# Three chunky glitch bursts spread across the loop.
BURSTS = (3.0, 6.6, 9.8)


def _glitch_offsets(axis_amplitude):
    """Discrete keyframes that jolt a channel sideways during each burst."""
    stops, values = [0.0], ["0"]
    for i, t in enumerate(BURSTS):
        shove = axis_amplitude if i % 2 == 0 else -axis_amplitude
        stops += [t, t + 0.06, t + 0.12, t + 0.18]
        values += [str(shove), str(-shove * 0.6), str(shove * 0.4), "0"]
    stops.append(LOOP)
    values.append("0")
    return keyframes(LOOP, stops), ";".join(values)


def _title_channel(fill, amplitude, opacity):
    times, values = _glitch_offsets(amplitude)
    return f"""<g opacity="{opacity}">
    <text x="0" y="0" font-family="{MONO}" font-size="84" font-weight="700"
          letter-spacing="4" fill="{fill}">{esc(TITLE)}
      <animate attributeName="x" values="{values}" keyTimes="{times}"
               dur="{LOOP}s" calcMode="discrete" repeatCount="indefinite"/>
    </text>
  </g>"""


def _rings(cx, cy):
    """Rotating instrument rings — the panel's heartbeat while text types."""
    return f"""<g transform="translate({cx} {cy})">
    <circle r="104" stroke="{RED}" stroke-width="1" stroke-dasharray="5 11" opacity="0.55">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360"
                        dur="24s" repeatCount="indefinite"/>
    </circle>
    <circle r="86" stroke="{CYAN}" stroke-width="1.5" stroke-dasharray="54 226" opacity="0.7">
      <animateTransform attributeName="transform" type="rotate" from="360" to="0"
                        dur="9s" repeatCount="indefinite"/>
    </circle>
    <circle r="68" stroke="{RED_DIM}" stroke-width="1" stroke-dasharray="2 7" opacity="0.8">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360"
                        dur="16s" repeatCount="indefinite"/>
    </circle>
    <path d="M0 0 L64 0 A64 64 0 0 1 32 55 Z" fill="url(#radarGrad)" opacity="0.5">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360"
                        dur="4.5s" repeatCount="indefinite"/>
    </path>
    <path d="M0 -44 L38 -22 L38 22 L0 44 L-38 22 L-38 -22 Z"
          stroke="{RED}" stroke-width="1.5" fill="{RED}" fill-opacity="0.05">
      <animate attributeName="fill-opacity" values="0.04;0.16;0.04" dur="3s" repeatCount="indefinite"/>
    </path>
    <circle r="5" fill="{RED}" filter="url(#hardGlow)">
      <animate attributeName="r" values="4;7;4" dur="1.6s" repeatCount="indefinite"/>
    </circle>
    <text x="0" y="150" font-family="{MONO}" font-size="17" letter-spacing="3"
          fill="{MUTED}" text-anchor="middle">SIGNAL  ACQUIRED</text>
  </g>"""


def render():
    title_start = 0.25
    sub_start, sub_dur = 1.0, 1.15
    line_start, line_dur, line_gap = 2.5, 0.5, 0.72

    clips, lines = [], []
    for i, (state, label, value) in enumerate(BOOT):
        y = 272 + i * 40
        begin = line_start + i * line_gap
        text = f"[ {state} ]  {label} {'.' * max(2, 30 - len(label))} {value}"
        width = int(len(text) * 14.4) + 14
        clips.append(typewriter(f"bootClip{i}", 60, y - 22, width, 32, begin, line_dur, LOOP))
        colour = RED if state == ">>" else MUTED
        accent = RED if state == ">>" else "#2EA043"
        lines.append(
            f'<g clip-path="url(#bootClip{i})">'
            f'<text x="60" y="{y}" font-family="{MONO}" font-size="23" fill="{colour}">'
            f'<tspan fill="{accent}">[ {esc(state)} ]</tspan>'
            f'<tspan fill="{TEXT}" opacity="0.85">  {esc(label)} </tspan>'
            f'<tspan fill="{MUTED}">{"." * max(2, 30 - len(label))}</tspan>'
            f'<tspan fill="{accent}"> {esc(value)}</tspan>'
            f"</text></g>"
        )

    sub_width = int(len(SUBTITLE) * 19.4) + 14
    clips.append(typewriter("subClip", 62, 174, sub_width, 38, sub_start, sub_dur, LOOP))

    # Park the caret at the end of the final boot line, where a shell leaves it.
    last = BOOT[-1]
    last_text = f"[ {last[0]} ]  {last[1]} {'.' * max(2, 30 - len(last[1]))} {last[2]}"
    cursor_x = 60 + int(len(last_text) * 14.4) + 8
    cursor_y = 272 + (len(BOOT) - 1) * 40 - 20
    cursor_begin = line_start + (len(BOOT) - 1) * line_gap + line_dur
    body = f"""{defs_common(W, H)}
<defs>
  <linearGradient id="radarGrad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{RED}" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="{RED}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="barFill" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{RED_DIM}"/>
    <stop offset="100%" stop-color="{RED}"/>
  </linearGradient>
  {"".join(clips)}
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
{grid(W, H, 40)}
<ellipse cx="200" cy="170" rx="480" ry="320" fill="url(#glowRed)"/>
<ellipse cx="1010" cy="230" rx="240" ry="240" fill="url(#glowRed)" opacity="0.6"/>

<g transform="translate(60 136)" filter="url(#softGlow)">
  {_title_channel(CYAN, 5, 0.75)}
  {_title_channel(RED, 4, 0.75)}
  <text x="0" y="0" font-family="{MONO}" font-size="84" font-weight="700"
        letter-spacing="4" fill="{TEXT}">{esc(TITLE)}</text>
</g>

<g clip-path="url(#subClip)">
  <text x="62" y="200" font-family="{MONO}" font-size="26" letter-spacing="2"
        fill="{RED}" opacity="0.95">{esc(SUBTITLE)}</text>
</g>

<rect x="60" y="224" width="0" height="3" fill="url(#edgeGrad)">
  <animate attributeName="width" values="0;0;700;700" keyTimes="{keyframes(LOOP, [0, 0.6, 1.6, LOOP])}"
           dur="{LOOP}s" repeatCount="indefinite"/>
</rect>

{"".join(lines)}

<g opacity="0">
  <rect x="60" y="448" width="700" height="4" fill="#12161F" rx="1.5"/>
  <rect x="60" y="448" width="0" height="4" fill="url(#barFill)" rx="1.5">
    <animate attributeName="width" values="0;0;700;700;0"
             keyTimes="{keyframes(LOOP, [0, 2.4, 7.2, LOOP * 0.985, LOOP])}"
             dur="{LOOP}s" repeatCount="indefinite"/>
  </rect>
  {fade_in(2.2, 0.3, LOOP)}
</g>

<g opacity="0">
  <rect x="{cursor_x}" y="{cursor_y}" width="13" height="26" fill="{RED}">
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.49;0.5;1"
             dur="1.1s" repeatCount="indefinite"/>
  </rect>
  {fade_in(cursor_begin, 0.15, LOOP)}
</g>

{_rings(1010, 230)}
{scanline(W, H, 7.0)}
{corner_brackets(W, H, 26, 12, RED, 0.7)}
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" stroke="{RED}" stroke-opacity="0.28" fill="none"/>"""

    return document(W, H, body, "Italodevjs — full-stack engineer and security engineer")
