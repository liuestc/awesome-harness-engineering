#!/usr/bin/env python3
"""
weekly_insight.py — Weekly AI Knowledge Synthesis
===================================================
每周日运行，用 MiniMax-M2.7（推理模型）对本周新增资源进行深度分析：
  1. 提炼本周最重要的新趋势
  2. 发现概念间的争议或矛盾
  3. 预测下周值得关注的方向
  4. 生成 data/weekly_insight.json
  5. 发送邮件摘要到配置的邮箱

Usage:
  python scripts/weekly_insight.py
"""

import json
import os
import sys
import logging
import smtplib
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
WEEKLY_INSIGHT_FILE = DATA_DIR / "weekly_insight.json"

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_CHAT_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"
REASONING_MODEL = "MiniMax-M2.7"   # Deep reasoning for weekly synthesis
FAST_MODEL = "MiniMax-M2.5"        # Fast model for formatting

NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")


def call_minimax(prompt: str, model: str = FAST_MODEL, max_tokens: int = 4096) -> str:
    """Call MiniMax API and return text response."""
    if not MINIMAX_API_KEY:
        return ""
    try:
        resp = requests.post(
            MINIMAX_CHAT_URL,
            headers={"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.4,
            },
            timeout=120
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log.error(f"MiniMax API error: {e}")
        return ""


def load_recent_resources(days: int = 7) -> dict:
    """Load resources added in the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = {"repositories": [], "articles": [], "people": [], "total": 0}

    for fname, key in [("repositories.json", "repositories"), ("articles.json", "articles"), ("people.json", "people")]:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            continue
        items = json.loads(fpath.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            continue
        for item in items:
            added_at = item.get("added_at", "")
            try:
                dt = datetime.fromisoformat(added_at.replace("Z", "+00:00"))
                if dt >= cutoff:
                    recent[key].append(item)
            except Exception:
                pass

    recent["total"] = sum(len(recent[k]) for k in ["repositories", "articles", "people"])
    return recent


def load_all_resources_summary() -> str:
    """Build a comprehensive summary of all resources for analysis."""
    lines = []

    for fname, label in [("repositories.json", "仓库"), ("articles.json", "文章"), ("people.json", "人物")]:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            continue
        items = json.loads(fpath.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            continue
        lines.append(f"\n=== {label} ({len(items)}个) ===")
        for item in items[:20]:  # Limit to avoid token overflow
            title = item.get("name") or item.get("title_zh") or item.get("name", "")
            summary = item.get("ai_summary_zh") or item.get("summary_zh") or item.get("contribution_zh", "")
            concepts = ", ".join(item.get("key_concepts", [])[:3])
            score = item.get("quality_score", "")
            lines.append(f"  - {title} (分数:{score}): {summary[:100]}... [概念: {concepts}]")

    return "\n".join(lines)


def generate_weekly_insight(recent: dict, all_summary: str) -> dict:
    """Use MiniMax-M2.7 to generate deep weekly insights."""
    week_str = datetime.now(timezone.utc).strftime("%Y年第%W周")

    # Build recent additions summary
    recent_lines = []
    for repo in recent["repositories"]:
        recent_lines.append(f"  [仓库] {repo.get('name', '')}: {repo.get('ai_summary_zh', '')[:80]}")
    for art in recent["articles"]:
        recent_lines.append(f"  [文章] {art.get('title_zh', '')}: {art.get('summary_zh', '')[:80]}")
    for person in recent["people"]:
        recent_lines.append(f"  [人物] {person.get('name', '')}: {person.get('contribution_zh', '')[:80]}")

    recent_text = "\n".join(recent_lines) if recent_lines else "本周无新增资源"

    # Deep reasoning prompt for M2.7
    deep_prompt = f"""你是 Harness Engineering 领域的顶级研究员。请对本周（{week_str}）的 Harness Engineering 生态进行深度分析。

## 本周新增资源（{recent['total']}个）：
{recent_text}

## 当前知识库全貌：
{all_summary[:3000]}

## 请完成以下深度分析（用 JSON 格式回复）：

{{
  "week": "{week_str}",
  "headline": "本周最重要的一句话总结（20字以内，吸引人）",
  "top_trends": [
    {{
      "title": "趋势标题",
      "description": "详细描述（100字）",
      "evidence": ["支撑证据1", "支撑证据2"],
      "impact": "high|medium|low"
    }}
  ],
  "key_insights": [
    "洞见1：...",
    "洞见2：...",
    "洞见3：..."
  ],
  "controversies": [
    {{
      "topic": "争议话题",
      "side_a": "观点A",
      "side_b": "观点B",
      "my_take": "我的判断"
    }}
  ],
  "next_week_focus": [
    "下周值得关注的方向1",
    "下周值得关注的方向2",
    "下周值得关注的方向3"
  ],
  "must_read": [
    {{
      "title": "本周必读资源标题",
      "reason": "推荐理由（50字）",
      "url": "链接"
    }}
  ],
  "concept_evolution": "本周哪个核心概念发生了重要演进？（100字）",
  "ecosystem_health": {{
    "score": 8.5,
    "comment": "生态健康度评估（50字）"
  }}
}}

只输出 JSON，不要其他内容。"""

    log.info(f"Calling MiniMax-M2.7 for deep weekly analysis...")
    raw = call_minimax(deep_prompt, model=REASONING_MODEL, max_tokens=8192)

    # Parse JSON
    try:
        # Extract JSON from response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            insight = json.loads(raw[start:end])
        else:
            raise ValueError("No JSON found in response")
    except Exception as e:
        log.error(f"Failed to parse insight JSON: {e}")
        insight = {
            "week": week_str,
            "headline": "Harness Engineering 生态持续演进",
            "top_trends": [],
            "key_insights": [raw[:200] if raw else "分析暂时不可用"],
            "controversies": [],
            "next_week_focus": [],
            "must_read": [],
            "concept_evolution": "",
            "ecosystem_health": {"score": 7.0, "comment": "数据收集中"},
        }

    # Add metadata
    insight["generated_at"] = datetime.now(timezone.utc).isoformat()
    insight["new_resources_count"] = recent["total"]
    insight["new_repositories"] = len(recent["repositories"])
    insight["new_articles"] = len(recent["articles"])

    return insight


def generate_email_html(insight: dict) -> str:
    """Generate beautiful HTML email from insight data."""
    week = insight.get("week", "本周")
    headline = insight.get("headline", "Harness Engineering 周报")
    trends = insight.get("top_trends", [])
    key_insights = insight.get("key_insights", [])
    next_focus = insight.get("next_week_focus", [])
    must_read = insight.get("must_read", [])
    health = insight.get("ecosystem_health", {})
    new_count = insight.get("new_resources_count", 0)

    trends_html = ""
    for t in trends[:3]:
        impact_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}.get(t.get("impact", "medium"), "#6b7280")
        trends_html += f"""
        <div style="margin-bottom:16px; padding:16px; background:#1a2744; border-radius:8px; border-left:3px solid {impact_color}">
          <div style="font-weight:bold; color:#e2e8f0; margin-bottom:6px;">{t.get('title', '')}</div>
          <div style="color:#94a3b8; font-size:14px;">{t.get('description', '')}</div>
        </div>"""

    insights_html = "".join([f'<li style="margin-bottom:8px; color:#94a3b8;">{i}</li>' for i in key_insights[:3]])
    focus_html = "".join([f'<li style="margin-bottom:6px; color:#94a3b8;">🎯 {f}</li>' for f in next_focus[:3]])
    must_read_html = ""
    for m in must_read[:2]:
        must_read_html += f"""
        <div style="margin-bottom:12px; padding:12px; background:#1a2744; border-radius:6px;">
          <a href="{m.get('url', '#')}" style="color:#60a5fa; text-decoration:none; font-weight:bold;">{m.get('title', '')}</a>
          <div style="color:#94a3b8; font-size:13px; margin-top:4px;">{m.get('reason', '')}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#0f1629; font-family: -apple-system, 'Noto Sans SC', sans-serif;">
  <div style="max-width:600px; margin:0 auto; padding:24px;">

    <!-- Header -->
    <div style="background:linear-gradient(135deg, #1e3a8a, #1e40af); border-radius:12px; padding:28px; margin-bottom:20px; text-align:center;">
      <div style="color:#93c5fd; font-size:12px; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;">
        ⚡ HARNESS ENGINEERING WEEKLY
      </div>
      <div style="color:#ffffff; font-size:24px; font-weight:bold; margin-bottom:8px;">{week}</div>
      <div style="color:#bfdbfe; font-size:16px;">{headline}</div>
      <div style="margin-top:16px; color:#93c5fd; font-size:13px;">
        本周新增 <strong style="color:#60a5fa">{new_count}</strong> 个资源 |
        生态健康度 <strong style="color:#34d399">{health.get('score', 'N/A')}/10</strong>
      </div>
    </div>

    <!-- Trends -->
    <div style="background:#0f1f3d; border-radius:12px; padding:20px; margin-bottom:16px;">
      <h3 style="color:#60a5fa; margin:0 0 16px 0; font-size:14px; text-transform:uppercase; letter-spacing:1px;">
        🔥 本周核心趋势
      </h3>
      {trends_html}
    </div>

    <!-- Key Insights -->
    <div style="background:#0f1f3d; border-radius:12px; padding:20px; margin-bottom:16px;">
      <h3 style="color:#60a5fa; margin:0 0 16px 0; font-size:14px; text-transform:uppercase; letter-spacing:1px;">
        💡 关键洞见
      </h3>
      <ul style="margin:0; padding-left:20px;">{insights_html}</ul>
    </div>

    <!-- Must Read -->
    {f'''<div style="background:#0f1f3d; border-radius:12px; padding:20px; margin-bottom:16px;">
      <h3 style="color:#60a5fa; margin:0 0 16px 0; font-size:14px; text-transform:uppercase; letter-spacing:1px;">
        📚 本周必读
      </h3>
      {must_read_html}
    </div>''' if must_read_html else ''}

    <!-- Next Week -->
    <div style="background:#0f1f3d; border-radius:12px; padding:20px; margin-bottom:16px;">
      <h3 style="color:#60a5fa; margin:0 0 16px 0; font-size:14px; text-transform:uppercase; letter-spacing:1px;">
        🔭 下周关注方向
      </h3>
      <ul style="margin:0; padding-left:20px;">{focus_html}</ul>
    </div>

    <!-- Footer -->
    <div style="text-align:center; color:#475569; font-size:12px; margin-top:20px;">
      <a href="https://liuestc.manus.space" style="color:#60a5fa; text-decoration:none;">
        🌐 访问 Awesome Harness Engineering
      </a>
      <br><br>
      由 MiniMax-M2.7 自动生成 · {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
    </div>
  </div>
</body>
</html>"""


def send_email(subject: str, html_content: str):
    """Send HTML email via SMTP."""
    if not all([NOTIFY_EMAIL, SMTP_USER, SMTP_PASS]):
        log.warning("Email config incomplete. Skipping email send.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = NOTIFY_EMAIL
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, NOTIFY_EMAIL, msg.as_string())

        log.info(f"Email sent to {NOTIFY_EMAIL}")
        return True
    except Exception as e:
        log.error(f"Email send failed: {e}")
        return False


def main():
    log.info("=== Weekly Insight Generator ===")

    # Load data
    recent = load_recent_resources(days=7)
    log.info(f"Recent resources: {recent['total']} total ({recent['repositories']} repos, {recent['articles']} articles)")

    all_summary = load_all_resources_summary()

    # Generate insight
    insight = generate_weekly_insight(recent, all_summary)

    # Save to file
    WEEKLY_INSIGHT_FILE.write_text(json.dumps(insight, ensure_ascii=False, indent=2))
    log.info(f"Weekly insight saved → {WEEKLY_INSIGHT_FILE}")

    # Generate and send email
    if NOTIFY_EMAIL:
        html = generate_email_html(insight)
        week = insight.get("week", "本周")
        headline = insight.get("headline", "")
        subject = f"⚡ Harness Engineering 周报 | {week} | {headline}"
        send_email(subject, html)

    # Print summary
    print(f"\n=== {insight.get('week', '')} 周报摘要 ===")
    print(f"标题: {insight.get('headline', '')}")
    print(f"新增资源: {insight.get('new_resources_count', 0)} 个")
    print(f"生态健康度: {insight.get('ecosystem_health', {}).get('score', 'N/A')}/10")
    if insight.get("key_insights"):
        print("\n关键洞见:")
        for ins in insight["key_insights"][:3]:
            print(f"  • {ins}")


if __name__ == "__main__":
    main()
