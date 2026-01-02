#!/usr/bin/env python3
import json
import os
import sys
import urllib.request


USERNAME = "ShoaibTaimur"
OUT_PATH = os.path.join("assets", "stats", "profile-stats.svg")


def fetch_json(url, token):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "profile-stats-generator")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        data = resp.read().decode("utf-8")
        return json.loads(data), resp.headers


def get_all_repos(token):
    repos = []
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
    while url:
        data, headers = fetch_json(url, token)
        repos.extend(data)
        link = headers.get("Link", "")
        next_url = None
        if link:
            parts = [p.strip() for p in link.split(",")]
            for part in parts:
                if 'rel="next"' in part:
                    next_url = part.split(";")[0].strip().strip("<>")
                    break
        url = next_url
    return repos


def render_profile_svg(stats, lang_totals):
    width = 640
    line_height = 18
    rows = max(1, (len(lang_totals) + 1) // 2)
    height = 220 + (rows * line_height) + 28
    bg = "#0f172a"
    card = "#111827"
    accent = "#38bdf8"
    text = "#e5e7eb"
    subtext = "#94a3b8"

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
        f'<rect x="16" y="16" width="{width - 32}" height="{height - 32}" rx="14" fill="{card}"/>',
        f'<text x="40" y="60" fill="{text}" font-size="20" font-family="Segoe UI, Ubuntu, Arial, sans-serif">GitHub Snapshot</text>',
        f'<text x="40" y="86" fill="{subtext}" font-size="12" font-family="Segoe UI, Ubuntu, Arial, sans-serif">@{USERNAME}</text>',
        f'<line x1="40" y1="100" x2="{width - 40}" y2="100" stroke="{accent}" stroke-width="2" opacity="0.5"/>',
        f'<text x="40" y="132" fill="{text}" font-size="14" font-family="Segoe UI, Ubuntu, Arial, sans-serif">Public Repos: {stats["public_repos"]}</text>',
        f'<text x="240" y="132" fill="{text}" font-size="14" font-family="Segoe UI, Ubuntu, Arial, sans-serif">Followers: {stats["followers"]}</text>',
        f'<text x="400" y="132" fill="{text}" font-size="14" font-family="Segoe UI, Ubuntu, Arial, sans-serif">Following: {stats["following"]}</text>',
        f'<text x="40" y="160" fill="{text}" font-size="14" font-family="Segoe UI, Ubuntu, Arial, sans-serif">Stars Earned: {stats["stars"]}</text>',
        f'<text x="240" y="160" fill="{text}" font-size="14" font-family="Segoe UI, Ubuntu, Arial, sans-serif">Forks: {stats["forks"]}</text>',
        f'<text x="40" y="188" fill="{subtext}" font-size="12" font-family="Segoe UI, Ubuntu, Arial, sans-serif">Updated by GitHub Actions</text>',
    ]
    items = sorted(lang_totals.items(), key=lambda kv: kv[1], reverse=True)
    if not items:
        items = [("No languages found", 0)]

    col_gap = 24
    col_width = (width - 80 - col_gap) // 2
    start_y = 228
    lines.append(
        f'<text x="40" y="212" fill="{text}" font-size="16" font-family="Segoe UI, Ubuntu, Arial, sans-serif">Language Usage</text>'
    )
    lines.append(
        f'<line x1="40" y1="220" x2="{width - 40}" y2="220" stroke="{accent}" stroke-width="2" opacity="0.35"/>'
    )
    for idx, (lang, bytes_count) in enumerate(items):
        col = idx // rows
        row = idx % rows
        x = 40 + (col * (col_width + col_gap))
        y = start_y + (row * line_height)
        label = f"{lang}: {bytes_count:,}"
        lines.append(
            f'<text x="{x}" y="{y}" fill="{text}" font-size="13" font-family="Segoe UI, Ubuntu, Arial, sans-serif">{label}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def main():
    token = os.environ.get("GITHUB_TOKEN")
    user_url = f"https://api.github.com/users/{USERNAME}"
    user_data, _ = fetch_json(user_url, token)
    repos = get_all_repos(token)
    stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    forks = sum(repo.get("forks_count", 0) for repo in repos)

    stats = {
        "public_repos": user_data.get("public_repos", 0),
        "followers": user_data.get("followers", 0),
        "following": user_data.get("following", 0),
        "stars": stars,
        "forks": forks,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    lang_totals = {}
    for repo in repos:
        lang_url = repo.get("languages_url")
        if not lang_url:
            continue
        data, _ = fetch_json(lang_url, token)
        for lang, count in data.items():
            lang_totals[lang] = lang_totals.get(lang, 0) + int(count)

    svg = render_profile_svg(stats, lang_totals)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error generating stats: {exc}")
        sys.exit(1)
