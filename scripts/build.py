#!/usr/bin/env python3
"""Render the profile masthead.

The banner in README.md is generated rather than hand-written SVG, so its
geometry and animation timings stay in one place. Run after editing anything
under scripts/render/.

    python3 scripts/build.py
"""

import pathlib
import sys
import xml.parsers.expat

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from render import hero  # noqa: E402

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"


def validate(path):
    """Parse the rendered file so malformed XML fails here, not in the browser."""
    parser = xml.parsers.expat.ParserCreate()
    try:
        parser.Parse(path.read_bytes(), True)
    except xml.parsers.expat.ExpatError as exc:
        raise SystemExit(f"[build] {path.name} is not well-formed XML: {exc}")


def main():
    ASSETS.mkdir(exist_ok=True)
    target = ASSETS / "hero.svg"
    target.write_text(hero.render(), encoding="utf-8")
    validate(target)
    print(f"[build] rendered and validated {target.name}")


if __name__ == "__main__":
    main()
