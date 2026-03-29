"""
GitHub Stars 更新脚本
每次爬虫运行时同步更新所有仓库的 Star 数量
"""

import os
import json
import logging
from pathlib import Path
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def update_github_stars():
    repos_path = DATA_DIR / "repositories.json"
    with open(repos_path, "r", encoding="utf-8") as f:
        repos = json.load(f)

    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    updated = 0
    for repo in repos:
        url = repo.get("url", "")
        if "github.com" not in url:
            continue
        # 提取 owner/repo
        parts = url.replace("https://github.com/", "").strip("/").split("/")
        if len(parts) < 2:
            continue
        owner, name = parts[0], parts[1]
        try:
            resp = requests.get(
                f"https://api.github.com/repos/{owner}/{name}",
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                repo["stars"] = data.get("stargazers_count", repo.get("stars"))
                repo["language"] = data.get("language") or repo.get("language", "")
                updated += 1
        except Exception as e:
            log.warning(f"Failed to update stars for {url}: {e}")

    with open(repos_path, "w", encoding="utf-8") as f:
        json.dump(repos, f, ensure_ascii=False, indent=2)
    log.info(f"Updated stars for {updated} repositories")


if __name__ == "__main__":
    update_github_stars()
