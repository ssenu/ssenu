"""README의 '최근 프로젝트 3개' 영역을 자동으로 갱신하는 스크립트.

GitHub API로 가장 최근에 수정된 레포 3개를 가져와,
README.md 의 <!-- RECENT:START --> ~ <!-- RECENT:END --> 사이를 갈아끼운다.
외부 라이브러리 없이 표준 라이브러리(urllib)만 사용한다.
"""

import json
import os
import re
import urllib.request

USER = "ssenu"            # GitHub 사용자명
TOP_N = 3                  # 보여줄 프로젝트 개수
README = "README.md"
START = "<!-- RECENT:START -->"
END = "<!-- RECENT:END -->"


def fetch_repos():
    """소유한(포크 아닌) 레포를 최근 수정순으로 가져온다."""
    url = (
        f"https://api.github.com/users/{USER}/repos"
        "?sort=updated&per_page=100&type=owner"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER,
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def build_block(repos):
    """레포 목록을 마크다운 표로 만든다 (외부 서버 의존 없음)."""
    # 프로필 레포(ssenu/ssenu) 자신과 포크는 제외
    repos = [r for r in repos if r["name"].lower() != USER.lower() and not r["fork"]]
    top = repos[:TOP_N]
    if not top:
        return "_아직 표시할 프로젝트가 없습니다._"
    lines = ["| Project | Description | Language |", "| :-- | :-- | :--: |"]
    for repo in top:
        name = repo["name"]
        url = repo["html_url"]
        desc = (repo.get("description") or "—").replace("|", "\\|")
        lang = repo.get("language") or "—"
        lines.append(f"| [{name}]({url}) | {desc} | {lang} |")
    return "\n".join(lines)


def main():
    repos = fetch_repos()
    block = build_block(repos)

    with open(README, encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    replacement = f"{START}\n\n{block}\n\n{END}"
    new_content = pattern.sub(replacement, content)

    if new_content != content:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README updated.")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
