#!/usr/bin/env python3
"""Compile the profile.

Reads the account's real state from the GitHub API, renders every panel in
`assets/` from scratch, and rewrites the live block inside README.md. Run by
`.github/workflows/heartbeat.yml` on a schedule, so the profile re-renders
itself instead of pointing at someone else's stats service.

    python3 scripts/build.py            # uses $GITHUB_TOKEN when present
"""

import datetime as dt
import json
import os
import pathlib
import sys
import xml.parsers.expat
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from render import hero, hud, pulse, stack  # noqa: E402

USER = os.environ.get("PROFILE_USER", "italodevjs")
TOKEN = os.environ.get("GH_GRAPHQL_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
SNAPSHOT = ROOT / "scripts" / "snapshot.json"
UTC_OFFSET = dt.timedelta(hours=-3)  # America/Sao_Paulo

LIVE_START = "<!-- LIVE:START -->"
LIVE_END = "<!-- LIVE:END -->"


def log(message):
    print(f"[build] {message}", flush=True)


def _request(url, data=None, headers=None):
    head = {"User-Agent": "italodevjs-profile-builder", "Accept": "application/vnd.github+json"}
    if TOKEN:
        head["Authorization"] = f"Bearer {TOKEN}"
    head.update(headers or {})
    payload = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=payload, headers=head)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode())


def fetch_profile():
    try:
        return _request(f"https://api.github.com/users/{USER}")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        log(f"profile unavailable ({exc}); using cached defaults")
        return {}


def fetch_repos():
    repos, page = [], 1
    while page <= 4:
        try:
            batch = _request(
                f"https://api.github.com/users/{USER}/repos"
                f"?per_page=100&page={page}&sort=pushed&type=owner"
            )
        except (urllib.error.URLError, OSError, ValueError) as exc:
            log(f"repo page {page} unavailable ({exc})")
            break
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return [r for r in repos if not r.get("fork")]


CALENDAR_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_calendar():
    """Daily contribution counts for the trailing year, oldest first."""
    if not TOKEN:
        log("no token in environment; cardiogram will render its awaiting-sync state")
        return []
    try:
        result = _request(
            "https://api.github.com/graphql",
            data={"query": CALENDAR_QUERY, "variables": {"login": USER}},
            headers={"Accept": "application/json"},
        )
    except (urllib.error.URLError, OSError, ValueError) as exc:
        log(f"calendar unavailable ({exc})")
        return []
    try:
        weeks = (result["data"]["user"]["contributionsCollection"]
                 ["contributionCalendar"]["weeks"])
    except (KeyError, TypeError):
        log(f"calendar response unusable: {str(result)[:200]}")
        return []
    return [(day["date"], day["contributionCount"])
            for week in weeks for day in week["contributionDays"]]


def calendar_stats(days):
    if not days:
        return {"total": "—", "peak": "—", "longest": "—", "current": "—"}
    counts = [c for _, c in days]
    longest = run = 0
    for count in counts:
        run = run + 1 if count else 0
        longest = max(longest, run)
    trailing = counts[:-1] if counts and counts[-1] == 0 else counts  # today may not be over yet
    current = 0
    for count in reversed(trailing):
        if not count:
            break
        current += 1
    return {
        "total": str(sum(counts)),
        "peak": str(max(counts)),
        "longest": f"{longest}d",
        "current": f"{current}d",
    }


def language_shares(repos):
    tally = {}
    for repo in repos:
        language = repo.get("language")
        if language:
            tally[language] = tally.get(language, 0) + 1
    total = sum(tally.values())
    if not total:
        return [("Awaiting sync", 1.0)]
    ranked = sorted(tally.items(), key=lambda kv: -kv[1])
    return [(name, count / total) for name, count in ranked]


def relative_time(iso, now):
    try:
        stamp = dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except (TypeError, ValueError):
        return "—"
    seconds = max(0, (now - stamp).total_seconds())
    for limit, divisor, unit in (
        (3600, 60, "min"), (86400, 3600, "h"), (2592000, 86400, "d"),
        (31536000, 2592000, "mo"),
    ):
        if seconds < limit:
            return f"{int(seconds // divisor)}{unit} ago"
    return f"{int(seconds // 31536000)}y ago"


def load_snapshot():
    """Last known-good API response, committed alongside the code.

    Lets a build survive an API outage or a rate limit with the previous
    numbers rather than a set of empty panels.
    """
    try:
        return json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_snapshot(profile, repos, days):
    payload = {
        "profile": {k: profile.get(k) for k in
                    ("public_repos", "followers", "created_at")},
        "repos": [{k: r.get(k) for k in
                   ("name", "language", "stargazers_count", "pushed_at")}
                  for r in repos],
        "calendar": days,
        "captured": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    SNAPSHOT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def collect(profile, repos):
    now = dt.datetime.now(dt.timezone.utc)
    # A cached snapshot may carry whatever order it was captured in; the
    # "recent pushes" panel only means anything sorted newest first.
    repos = sorted(repos, key=lambda r: r.get("pushed_at") or "", reverse=True)
    created = profile.get("created_at", "")
    years = "—"
    if created[:4].isdigit():
        years = f"{max(1, now.year - int(created[:4]))}+"
    return {
        "languages": language_shares(repos),
        "repos": profile.get("public_repos", len(repos)) or len(repos),
        "followers": profile.get("followers", "—"),
        "stars": sum(r.get("stargazers_count", 0) for r in repos),
        "years": years,
        "synced": (now + UTC_OFFSET).strftime("%Y-%m-%d %H:%M BRT"),
        "recent": [
            (r["name"], r.get("language"), relative_time(r.get("pushed_at"), now))
            for r in repos[:5]
        ] or [("awaiting first sync", None, "—")],
        "repo_objects": repos,
        "now": now,
    }


def live_markdown(data, days, stats):
    """The self-updating block inside README.md.

    Deliberately free of tables: GitHub squeezes them to one word per line on a
    phone, and most profile visits are on a phone.
    """
    local = (data["now"] + UTC_OFFSET).strftime("%d %b %Y · %H:%M")
    active = sum(1 for _, c in days if c) if days else "—"
    total = stats["total"]
    if total.isdigit():
        total = f"{int(total):,}"
    rows = []
    for name, language, when in data["recent"][:3]:
        if when == "—":
            rows.append(f"`{name}`")
        else:
            rows.append(
                f"[`{name}`](https://github.com/{USER}/{name})"
                f" · {language or 'no primary language'} · {when}"
            )
    pushes = "<br/>".join(rows)
    stars = data["stars"]
    star_word = "star" if stars == 1 else "stars"
    return "\n".join([
        LIVE_START,
        "",
        f"**{data['repos']}** public repos &nbsp;·&nbsp; **{stars}** {star_word}"
        f" &nbsp;·&nbsp; **{data['followers']}** followers",
        "",
        f"**{total}** contributions in the last year, across **{active}** active days.",
        "",
        "**Latest pushes**",
        "",
        pushes,
        "",
        f"<sub>rebuilt automatically · last sync {local} BRT</sub>",
        "",
        LIVE_END,
    ])


def rewrite_readme(block):
    if not README.exists():
        log("README.md missing; skipping injection")
        return
    text = README.read_text(encoding="utf-8")
    if LIVE_START not in text or LIVE_END not in text:
        log("live markers absent; skipping injection")
        return
    head, rest = text.split(LIVE_START, 1)
    _, tail = rest.split(LIVE_END, 1)
    README.write_text(head + block + tail, encoding="utf-8")
    log("README live block updated")


def validate(path):
    """Parse a rendered panel before it is allowed to ship.

    The workflow commits whatever this script writes, so a renderer that emits
    malformed XML would publish a broken image straight to the profile. Parsing
    here turns that into a failed build instead.
    """
    parser = xml.parsers.expat.ParserCreate()
    try:
        parser.Parse(path.read_bytes(), True)
    except xml.parsers.expat.ExpatError as exc:
        raise SystemExit(f"[build] {path.name} is not well-formed XML: {exc}")


def main():
    ASSETS.mkdir(exist_ok=True)
    profile, repos, days = fetch_profile(), fetch_repos(), fetch_calendar()

    if profile and repos:
        save_snapshot(profile, repos, days)
    else:
        cached = load_snapshot()
        profile = profile or cached.get("profile", {})
        repos = repos or cached.get("repos", [])
        days = days or cached.get("calendar", [])
        if repos:
            log(f"serving cached snapshot from {cached.get('captured', 'unknown time')}")

    data = collect(profile, repos)
    stats = calendar_stats(days)

    panels = {
        "hero.svg": hero.render(),
        "stack.svg": stack.render(),
        "hud.svg": hud.render(data),
        "pulse.svg": pulse.render(days, stats),
    }
    for name, markup in panels.items():
        target = ASSETS / name
        target.write_text(markup, encoding="utf-8")
        validate(target)
    log(f"rendered and validated {len(panels)} panels · {len(days)} calendar days"
        f" · {len(data['repo_objects'])} repos")

    rewrite_readme(live_markdown(data, days, stats))


if __name__ == "__main__":
    main()
