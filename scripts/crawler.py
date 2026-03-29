"""
Harness Engineering Resource Crawler
=====================================
每日定时运行，通过 Tavily 搜索 + GitHub API 发现新资源，
使用 MiniMax 2.7 进行智能分析、去重、评分和内容提炼。

环境变量（通过 GitHub Secrets 注入）:
  TAVILY_API_KEY    - Tavily 搜索 API Key
  MINIMAX_API_KEY   - MiniMax 2.7 API Key
  GITHUB_TOKEN      - GitHub Actions 自动注入
  NOTIFY_EMAIL      - 失败通知邮箱（可选）
"""

import os
import json
import uuid
import hashlib
import logging
import smtplib
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

# ── 配置 ──────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "1063506577@qq.com")

# MiniMax API 配置
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"
# M2.5 用于分析任务（非推理模型，响应快、适合结构化输出）
# M2.7 是推理模型，适合复杂推理但 token 消耗大
MINIMAX_MODEL = "MiniMax-M2.5"

# 搜索关键词列表（尽可能全面覆盖 Harness Engineering 生态）
SEARCH_KEYWORDS = [
    "harness engineering AI agent",
    "agent harness design pattern",
    "claude code harness AGENTS.md",
    "context engineering coding agent",
    "coding agent orchestration workflow",
    "agentic coding scaffold framework",
    "LLM agent loop design",
    "autonomous coding agent harness",
    "ralph wiggum technique agent",
    "generator evaluator agent architecture",
    "agent context management best practice",
    "AI agent observability logging",
    "agent skill system MCP server",
    "sub-agent orchestration context firewall",
    "agent hook system deterministic",
    "vibe coding harness engineering difference",
    "agent first software development",
    "AGENTS.md best practice template",
    "coding agent feedback loop",
    "AI pair programming workflow automation",
    "software engineering AI agent 2026",
    "claude code workflow productivity",
    "openai codex agent harness",
    "anthropic claude agent engineering",
    "langchain agent harness improvement",
]

# GitHub 搜索查询
GITHUB_SEARCH_QUERIES = [
    "harness engineering agent",
    "AGENTS.md claude code",
    "agent harness scaffold",
    "coding agent orchestration",
    "ralph wiggum loop agent",
]

MAX_NEW_ITEMS_PER_RUN = 15
QUALITY_THRESHOLD = 6.0
NEW_ITEM_DAYS_BADGE = 7  # 7天内新增的标记为 New


# ── 数据加载 ──────────────────────────────────────────────────────────────────

def load_data(filename: str) -> list | dict:
    path = DATA_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return [] if filename != "meta.json" else {}


def save_data(filename: str, data: list | dict):
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"Saved {filename}")


def get_existing_urls() -> set:
    """获取所有已存在资源的 URL，用于去重"""
    urls = set()
    for filename in ["repositories.json", "articles.json", "people.json"]:
        items = load_data(filename)
        for item in items:
            url = item.get("url", "")
            if url:
                urls.add(url.rstrip("/").lower())
    return urls


# ── Tavily 搜索 ───────────────────────────────────────────────────────────────

def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    """使用 Tavily API 搜索，返回结果列表"""
    if not TAVILY_API_KEY:
        log.warning("TAVILY_API_KEY not set, skipping search")
        return []
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "advanced",
                "include_raw_content": True,
                "max_results": max_results,
                "include_domains": [],
                "exclude_domains": [],
            },
            timeout=30,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        log.info(f"Tavily [{query[:40]}]: {len(results)} results")
        return results
    except Exception as e:
        log.error(f"Tavily search error for '{query}': {e}")
        return []


def github_search_repos(query: str, max_results: int = 5) -> list[dict]:
    """使用 GitHub Search API 搜索仓库"""
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    try:
        resp = requests.get(
            "https://api.github.com/search/repositories",
            params={
                "q": f"{query} in:name,description,readme",
                "sort": "updated",
                "order": "desc",
                "per_page": max_results,
            },
            headers=headers,
            timeout=20,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        log.info(f"GitHub [{query}]: {len(items)} repos")
        return items
    except Exception as e:
        log.error(f"GitHub search error for '{query}': {e}")
        return []


def fetch_full_content(url: str, raw_content: str = "") -> str:
    """尝试获取页面全文，优先使用 Tavily 返回的 raw_content"""
    if raw_content and len(raw_content) > 200:
        return raw_content[:8000]  # 截断至 8K 字符
    # 简单 HTTP 抓取（仅用于 GitHub README 等）
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "HarnessBot/1.0"})
        if resp.status_code == 200:
            return resp.text[:8000]
    except Exception:
        pass
    return ""


# ── MiniMax 分析 ──────────────────────────────────────────────────────────────

def minimax_chat(messages: list[dict], temperature: float = 0.3) -> str:
    """调用 MiniMax 2.7 API"""
    if not MINIMAX_API_KEY:
        log.warning("MINIMAX_API_KEY not set")
        return ""
    try:
        resp = requests.post(
            MINIMAX_API_URL,
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MINIMAX_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 8192,  # 推理模型需要更大空间，reasoning_content 会消耗大量 token
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        # 检查 base_resp 状态
        base = data.get("base_resp", {})
        if base.get("status_code", 0) != 0:
            log.error(f"MiniMax API error code {base.get('status_code')}: {base.get('status_msg')}")
            return ""
        choices = data.get("choices")
        if not choices:
            log.error(f"MiniMax returned no choices: {data}")
            return ""
        return choices[0]["message"]["content"]
    except Exception as e:
        log.error(f"MiniMax API error: {e}")
        return ""


def analyze_resource(title: str, url: str, content: str, resource_type: str = "auto") -> dict | None:
    """
    使用 MiniMax 分析资源，返回结构化数据。
    返回 None 表示质量不达标或不相关。
    """
    prompt = f"""你是 Harness Engineering 领域的专家研究员。请分析以下资源并判断其是否与 Harness Engineering 相关。

Harness Engineering 定义：围绕 AI Agent 构建约束机制、反馈回路和持续改进循环的系统工程实践。
核心公式：Agent = Model + Harness
相关主题：AGENTS.md、Context Engineering、Agent Orchestration、Coding Agent、Ralph Wiggum Loop、Generator-Evaluator、MCP Server、Agent Skills、Autonomous Coding 等。

资源信息：
- 标题：{title}
- URL：{url}
- 内容摘要：{content[:3000]}

请以 JSON 格式返回分析结果（只返回 JSON，不要其他文字）：
{{
  "is_relevant": true/false,
  "resource_type": "repository/article/person/tool",
  "quality_score": 0-10的浮点数（相关性+质量+新颖性综合评分，6分以上才有价值）,
  "title_zh": "中文标题",
  "title_en": "English title",
  "summary_zh": "50-100字中文摘要",
  "summary_en": "50-100 word English summary",
  "key_concepts": ["概念1", "概念2", "概念3"],
  "category": "分类（如：框架/工具、教程/学习、最佳实践、Awesome List、文章/博客等）",
  "tags": ["tag1", "tag2", "tag3"],
  "cluster": "所属知识图谱簇（如：foundations/context-engineering/feedback-loops/best-practices/tools/frameworks/analysis/performance/observability）",
  "relations_hint": "与哪些已知资源相关（可为空字符串）",
  "key_insights_zh": ["洞见1", "洞见2"],
  "key_insights_en": ["insight1", "insight2"]
}}"""

    result_str = minimax_chat([{"role": "user", "content": prompt}])
    if not result_str:
        return None

    # 提取 JSON
    try:
        # 去掉 markdown 代码块
        if "```json" in result_str:
            result_str = result_str.split("```json")[1].split("```")[0].strip()
        elif "```" in result_str:
            result_str = result_str.split("```")[1].split("```")[0].strip()
        data = json.loads(result_str)
    except json.JSONDecodeError:
        log.warning(f"Failed to parse MiniMax response for {url}")
        return None

    if not data.get("is_relevant", False):
        log.info(f"Not relevant: {url}")
        return None

    score = float(data.get("quality_score", 0))
    if score < QUALITY_THRESHOLD:
        log.info(f"Quality too low ({score}): {url}")
        return None

    return data


def build_resource_item(url: str, analysis: dict, raw_content: str, stars: int | None = None) -> dict:
    """根据分析结果构建标准化资源条目"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    resource_type = analysis.get("resource_type", "article")

    # 生成唯一 ID
    prefix_map = {"repository": "repo", "article": "art", "person": "person", "tool": "tool"}
    prefix = prefix_map.get(resource_type, "res")
    uid = f"{prefix}-{hashlib.md5(url.encode()).hexdigest()[:8]}"

    item = {
        "id": uid,
        "url": url,
        "added_at": today,
        "updated_at": today,
        "quality_score": analysis.get("quality_score", 7.0),
        "category": analysis.get("category", "其他"),
        "tags": analysis.get("tags", []),
        "key_concepts": analysis.get("key_concepts", []),
        "raw_content": raw_content[:4000] if raw_content else "",
        "relations": [],
        "embeddings_ready": False,
        "graph_node": {
            "type": resource_type,
            "cluster": analysis.get("cluster", "general")
        }
    }

    if resource_type == "repository":
        item.update({
            "name": url.replace("https://github.com/", ""),
            "description_zh": analysis.get("summary_zh", ""),
            "description_en": analysis.get("summary_en", ""),
            "stars": stars,
            "language": "英文",
            "ai_summary_zh": analysis.get("summary_zh", ""),
            "ai_summary_en": analysis.get("summary_en", ""),
        })
    else:
        item.update({
            "title_zh": analysis.get("title_zh", ""),
            "title_en": analysis.get("title_en", ""),
            "author": "",
            "organization": "",
            "date": today,
            "summary_zh": analysis.get("summary_zh", ""),
            "summary_en": analysis.get("summary_en", ""),
            "key_insights_zh": analysis.get("key_insights_zh", []),
            "key_insights_en": analysis.get("key_insights_en", []),
            "ai_summary_zh": analysis.get("summary_zh", ""),
            "ai_summary_en": analysis.get("summary_en", ""),
        })

    return item


# ── 主流程 ────────────────────────────────────────────────────────────────────

def run_pipeline() -> dict:
    """
    主爬取和分析流程。
    返回运行报告。
    """
    log.info("=" * 60)
    log.info("Harness Engineering Crawler — Starting")
    log.info("=" * 60)

    existing_urls = get_existing_urls()
    log.info(f"Existing resources: {len(existing_urls)} URLs")

    new_repos = []
    new_articles = []
    candidates = []  # (url, title, content, stars, source_type)

    # ── Step 1: Tavily 搜索 ──
    log.info("Step 1: Tavily search...")
    seen_urls = set()
    for keyword in SEARCH_KEYWORDS:
        results = tavily_search(keyword, max_results=5)
        for r in results:
            url = r.get("url", "").rstrip("/")
            if not url or url.lower() in existing_urls or url in seen_urls:
                continue
            seen_urls.add(url)
            title = r.get("title", "")
            raw = r.get("raw_content", "") or r.get("content", "")
            # 判断是否为 GitHub 仓库
            source_type = "repository" if "github.com" in url and url.count("/") >= 4 else "article"
            candidates.append((url, title, raw, None, source_type))

    # ── Step 2: GitHub 搜索 ──
    log.info("Step 2: GitHub repository search...")
    for query in GITHUB_SEARCH_QUERIES:
        repos = github_search_repos(query, max_results=5)
        for repo in repos:
            url = repo.get("html_url", "").rstrip("/")
            if not url or url.lower() in existing_urls or url in seen_urls:
                continue
            seen_urls.add(url)
            title = repo.get("full_name", "")
            raw = repo.get("description", "") or ""
            stars = repo.get("stargazers_count", None)
            candidates.append((url, title, raw, stars, "repository"))

    log.info(f"Total candidates: {len(candidates)}")

    # ── Step 3: MiniMax 分析 ──
    log.info("Step 3: MiniMax analysis...")
    analyzed_items = []
    for url, title, raw_content, stars, source_type in candidates:
        if len(analyzed_items) >= MAX_NEW_ITEMS_PER_RUN:
            break
        log.info(f"Analyzing: {url[:80]}")
        # 尝试获取全文
        full_content = fetch_full_content(url, raw_content)
        analysis = analyze_resource(title, url, full_content, source_type)
        if analysis is None:
            continue
        item = build_resource_item(url, analysis, full_content, stars)
        analyzed_items.append((item, analysis.get("resource_type", "article")))
        log.info(f"  ✓ Accepted: score={analysis.get('quality_score')}, type={analysis.get('resource_type')}")

    # ── Step 4: 分类存储 ──
    log.info("Step 4: Saving new items...")
    repos_data = load_data("repositories.json")
    articles_data = load_data("articles.json")
    people_data = load_data("people.json")

    added_count = {"repository": 0, "article": 0, "person": 0, "tool": 0}
    recent_additions = []

    for item, rtype in analyzed_items:
        if rtype == "repository":
            repos_data.append(item)
            new_repos.append(item)
            added_count["repository"] += 1
        elif rtype == "person":
            people_data.append(item)
            added_count["person"] += 1
        else:
            articles_data.append(item)
            new_articles.append(item)
            added_count["article"] += 1

        recent_additions.append({
            "id": item["id"],
            "type": rtype,
            "title_zh": item.get("title_zh") or item.get("name") or item.get("description_zh", "")[:40],
            "title_en": item.get("title_en") or item.get("name") or item.get("description_en", "")[:40],
            "added_at": item["added_at"],
            "url": item["url"],
        })

    save_data("repositories.json", repos_data)
    save_data("articles.json", articles_data)
    save_data("people.json", people_data)

    # ── Step 5: 更新 meta.json ──
    meta = load_data("meta.json")
    meta["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta["stats"] = {
        "repositories": len(repos_data),
        "articles": len(articles_data),
        "people": len(people_data),
        "total_resources": len(repos_data) + len(articles_data) + len(people_data),
    }
    # 保留最近 10 条新增
    existing_recent = meta.get("recent_additions", [])
    meta["recent_additions"] = (recent_additions + existing_recent)[:10]
    save_data("meta.json", meta)

    total_added = sum(added_count.values())
    report = {
        "success": True,
        "run_at": meta["last_updated"],
        "candidates_found": len(candidates),
        "items_added": total_added,
        "breakdown": added_count,
        "new_repos": [r.get("name", r.get("url")) for r in new_repos],
        "new_articles": [a.get("title_zh", a.get("url")) for a in new_articles],
    }
    log.info(f"Done! Added {total_added} new items: {added_count}")
    return report


# ── 邮件通知 ──────────────────────────────────────────────────────────────────

def send_failure_email(error_msg: str):
    """发送失败通知邮件（使用 GitHub Actions SMTP 或 QQ 邮件）"""
    if not NOTIFY_EMAIL:
        return
    # 使用 GitHub Actions 的 sendgrid 或直接 SMTP
    # 这里使用简单的 SMTP 方式，通过 QQ 邮箱
    smtp_host = os.environ.get("SMTP_HOST", "smtp.qq.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")

    if not smtp_user or not smtp_pass:
        log.warning("SMTP credentials not configured, skipping email notification")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = NOTIFY_EMAIL
        msg["Subject"] = "⚠️ Harness Engineering Crawler 运行失败"
        body = f"""
Harness Engineering 自动爬虫运行失败！

时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

错误信息：
{error_msg}

请检查 GitHub Actions 日志获取详细信息：
https://github.com/YOUR_USERNAME/awesome-harness-engineering/actions
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        log.info(f"Failure notification sent to {NOTIFY_EMAIL}")
    except Exception as e:
        log.error(f"Failed to send email: {e}")


def send_success_email(report: dict):
    """发送成功运行摘要邮件"""
    smtp_host = os.environ.get("SMTP_HOST", "smtp.qq.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")

    if not smtp_user or not smtp_pass:
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = NOTIFY_EMAIL
        msg["Subject"] = f"✅ Harness Engineering Crawler 运行完成 — 新增 {report['items_added']} 条资源"
        new_repos_list = "\n".join([f"  - {r}" for r in report.get("new_repos", [])]) or "  无"
        new_articles_list = "\n".join([f"  - {a}" for a in report.get("new_articles", [])]) or "  无"
        body = f"""
Harness Engineering 自动爬虫运行完成！

运行时间：{report['run_at']}
发现候选资源：{report['candidates_found']} 条
新增资源：{report['items_added']} 条
  - 仓库：{report['breakdown'].get('repository', 0)} 个
  - 文章：{report['breakdown'].get('article', 0)} 篇
  - 人物：{report['breakdown'].get('person', 0)} 位

新增仓库：
{new_repos_list}

新增文章：
{new_articles_list}

查看网站：https://YOUR_USERNAME.github.io/awesome-harness-engineering
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        log.info(f"Success notification sent to {NOTIFY_EMAIL}")
    except Exception as e:
        log.error(f"Failed to send email: {e}")


# ── 入口 ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        report = run_pipeline()
        log.info(json.dumps(report, ensure_ascii=False, indent=2))
        if report.get("items_added", 0) > 0:
            send_success_email(report)
    except Exception as e:
        error_msg = traceback.format_exc()
        log.error(f"Pipeline failed:\n{error_msg}")
        send_failure_email(error_msg)
        raise
