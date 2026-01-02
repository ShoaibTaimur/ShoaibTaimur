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


def render_svg(stats):
    width = 640
    height = 220
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
        "</svg>",
    ]
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
    svg = render_svg(stats)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error generating stats: {exc}")
        sys.exit(1)
