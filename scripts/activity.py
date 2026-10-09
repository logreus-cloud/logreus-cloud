import html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection { contributionCalendar { totalContributions } }
    recent: repositories(first: 10, privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes { name pushedAt primaryLanguage { name color } }
    }
    publicRepos: repositories(first: 1, privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
  }
}"""

PALETTES = {
    "dark": {
        "bg": "#000000", "scan": "#ffffff", "scan_op": "0.02",
        "line": "#dfe6ec", "glass": "#e8f0f6", "glass_op": "0.10",
        "main": "#c3cbd3", "sub": "#6b737c", "accent": "#7f9bb0",
        "rule2": "#3b444d", "chip_bg": "#0b0e12", "chip_st": "#2b333b",
        "chip_tx": "#aab3bd", "frame": "#1e242a",
    },
    "light": {
        "bg": "#f6f8fa", "scan": "#1f2328", "scan_op": "0.018",
        "line": "#57606a", "glass": "#57606a", "glass_op": "0.09",
        "main": "#2f363d", "sub": "#6e7781", "accent": "#4b6a82",
        "rule2": "#d0d7de", "chip_bg": "#ffffff", "chip_st": "#d0d7de",
        "chip_tx": "#57606a", "frame": "#d0d7de",
    },
}
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', 'Liberation Mono', monospace"

def fetch(login, token):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode("utf-8"),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise ValueError(f"GraphQL: {payload['errors']}")
    user = payload["data"]["user"]
    if user is None:
        raise ValueError(f"GitHub user not found: {login}")
    contributions = user["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    public_repos = user["publicRepos"]["totalCount"]
    repo = next((node for node in user["recent"]["nodes"] if node and node["pushedAt"] and node["name"].casefold() != login.casefold()), None)
    return contributions, public_repos, repo

def render(palette, contributions, public_repos, repo):
    p = PALETTES[palette]
    name = repo["name"] if repo else "—"
    short_name = name[:17] + "…" if len(name) > 18 else name
    pushed = datetime.fromisoformat(repo["pushedAt"].replace("Z", "+00:00")).astimezone(timezone.utc).date().isoformat() if repo else "n/a"
    language = repo.get("primaryLanguage") if repo else None
    color = language.get("color") if language else None
    if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        color = "#8b949e"
    language_dot = f'<circle cx="54" cy="89" r="6" fill="{color}"/>' if repo else ""
    esc = html.escape
    scans = "".join(f'<rect x="0" y="{y}" width="1200" height="2"/>' for y in range(0, 150, 18))
    label = esc(f"Last shipped: {name}, {pushed}. Contributions in the last 12 months: {contributions}. Public repos: {public_repos}.", quote=True)
    font = esc(FONT, quote=True)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 150" width="1200" height="150" role="img" aria-label="{label}">
  <defs>
    <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{p['glass']}" stop-opacity="{p['glass_op']}"/>
      <stop offset="1" stop-color="{p['glass']}" stop-opacity="0.02"/>
    </linearGradient>
    <clipPath id="card"><rect x="0" y="0" width="1200" height="150" rx="12"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="1200" height="150" fill="{p['bg']}"/>
    <g fill="{p['scan']}" opacity="{p['scan_op']}">{scans}</g>
    <g stroke="{p['line']}" fill="none" stroke-width="1">
      <polyline stroke-opacity="0.30" points="968,0 952,34 974,58 948,92 962,118 944,150"/>
      <polyline stroke-opacity="0.16" points="974,58 1010,70 1046,62"/>
      <polyline stroke-opacity="0.14" points="948,92 914,104 890,98"/>
      <polyline stroke-opacity="0.10" points="952,34 924,26"/>
    </g>
    <g stroke="{p['line']}" stroke-opacity="0.2" stroke-width="1">
      <polygon points="1010,22 1052,12 1042,46 1004,44" fill="url(#glass)"/>
      <polygon points="1096,92 1130,84 1124,122 1090,116" fill="url(#glass)"/>
    </g>
    <rect x="48" y="30" width="96" height="24" rx="4" fill="{p['chip_bg']}" stroke="{p['chip_st']}"/>
    <text x="96" y="46.5" text-anchor="middle" font-family="{font}" font-size="12" letter-spacing="1.5" fill="{p['chip_tx']}">LIVE · 01</text>
    <text x="162" y="49" font-family="{font}" font-size="13" fill="{p['sub']}">// updated daily by github actions</text>
    {language_dot}
    <text x="70" y="98" font-family="{font}" font-size="28" fill="{p['main']}">{esc(short_name)}</text>
    <rect x="48" y="110" width="64" height="2" fill="{p['accent']}" opacity="0.8"/>
    <rect x="118" y="110" width="390" height="2" fill="{p['rule2']}"/>
    <text x="48" y="128" font-family="{font}" font-size="13" fill="{p['sub']}">last shipped · {esc(pushed)}</text>
    <text x="560" y="98" font-family="{font}" font-size="28" fill="{p['main']}">{esc(str(contributions))}</text>
    <text x="560" y="128" font-family="{font}" font-size="13" fill="{p['sub']}">contributions · last 12 months</text>
    <text x="820" y="98" font-family="{font}" font-size="28" fill="{p['main']}">{esc(str(public_repos))}</text>
    <text x="820" y="128" font-family="{font}" font-size="13" fill="{p['sub']}">public repos</text>
    <rect x="0.5" y="0.5" width="1199" height="149" rx="12" fill="none" stroke="{p['frame']}"/>
  </g>
</svg>
"""

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is required")
    login = os.environ.get("GH_USER", "logreus-cloud")
    contributions, public_repos, repo = fetch(login, token)
    dark = render("dark", contributions, public_repos, repo)
    light = render("light", contributions, public_repos, repo)
    assets = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(assets, exist_ok=True)
    for filename, svg in (("activity.svg", dark), ("activity-light.svg", light)):
        with open(os.path.join(assets, filename), "w", encoding="utf-8", newline="\n") as output:
            output.write(svg)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"activity: {exc}", file=sys.stderr)
        sys.exit(1)
