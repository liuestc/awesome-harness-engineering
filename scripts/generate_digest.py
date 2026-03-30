#!/usr/bin/env python3
"""
每日小红书图文生成器 v2 — Gemini 背景 + Pillow 文字叠加
流程：
  1. MiniMax-M2.7 提炼今日内容 → digest.json
  2. Gemini 2.5 Flash Image 为每张卡片生成专属背景图
  3. Pillow 在背景图上叠加中文文字、标签、装饰元素
  4. 输出 7 张 1080×1350 PNG 卡片
"""

import json, os, sys, re, base64, time, requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO

# ── 路径 ──────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR  = REPO_ROOT / "data"
DIGEST_DIR = DATA_DIR / "daily_digest"

# ── API ──────────────────────────────────────────────────
MINIMAX_API_KEY  = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_API_URL  = "https://api.minimax.chat/v1/text/chatcompletion_v2"
MINIMAX_MODEL    = "MiniMax-M2.7"

GEMINI_API_KEY   = os.environ.get("GEMINI_API_KEY", "")
GEMINI_IMG_MODEL = "gemini-2.5-flash-image"
GEMINI_IMG_URL   = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_IMG_MODEL}:generateContent"

# ── 字体 ──────────────────────────────────────────────────
FONT_BLACK  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_BOLD   = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG    = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SERIF  = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
FONT_SERIF_B= "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

W, H = 1080, 1350

# ── 配色 ──────────────────────────────────────────────────
WHITE      = (255, 255, 255)
WHITE90    = (255, 255, 255, 230)
WHITE70    = (255, 255, 255, 178)
WHITE50    = (255, 255, 255, 128)
WHITE20    = (255, 255, 255, 51)
BLACK60    = (0, 0, 0, 153)
BLACK80    = (0, 0, 0, 204)

ACCENT_COLORS = [
    (100, 200, 255),   # 冰蓝
    (80,  240, 180),   # 青绿
    (255, 220, 80),    # 金黄
    (200, 120, 255),   # 紫罗兰
    (255, 140, 100),   # 珊瑚橙
]

# ── Gemini 背景图提示词 ───────────────────────────────────
BG_PROMPTS = {
    "cover": (
        "Ultra-detailed dark technology background for a social media card. "
        "Deep navy blue (#0a0f1e) base with glowing electric blue circuit board traces, "
        "scattered luminous particles, subtle hexagonal grid overlay, soft lens flare in top-right. "
        "Cinematic lighting, 8K quality, no text, no people, vertical 4:5 ratio. "
        "Bottom third is darker for text overlay."
    ),
    "insight_1": (
        "Abstract dark background: deep space navy with glowing neural network nodes connected by "
        "thin electric blue lines, soft bokeh light orbs, subtle data flow animation feel. "
        "Left side has a bright vertical accent stripe in electric blue. "
        "No text, vertical format, cinematic quality."
    ),
    "insight_2": (
        "Dark tech background: deep midnight blue with glowing green-teal circuit patterns, "
        "matrix-style falling code particles (very subtle), soft emerald glow in corners. "
        "Clean dark area in center-bottom for text. No text, vertical format."
    ),
    "insight_3": (
        "Abstract dark background: deep indigo-navy with golden-amber geometric patterns, "
        "constellation-like star map with connecting lines, warm amber glow emanating from center. "
        "Mystical yet technical feel. No text, vertical format, high quality."
    ),
    "insight_4": (
        "Dark futuristic background: deep navy with purple-violet energy waves, "
        "holographic grid lines, glowing purple nodes, cyberpunk aesthetic. "
        "Dramatic lighting from top-left. No text, vertical format."
    ),
    "insight_5": (
        "Dark tech background: deep space blue with coral-orange data visualization elements, "
        "abstract flowing data streams, warm orange glow, network topology feel. "
        "Clean dark zones for text overlay. No text, vertical format."
    ),
    "summary": (
        "Premium dark background: deep navy with rainbow gradient accent bar at top, "
        "subtle grid texture, multiple soft colored glows (blue, cyan, gold, purple), "
        "professional tech magazine aesthetic. Clean and elegant. No text, vertical format."
    ),
}

# ── 工具函数 ──────────────────────────────────────────────

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype(FONT_REG, size)
        except Exception:
            return ImageFont.load_default()

def wrap_text_pil(draw, text, font, max_width):
    """中文自动换行"""
    lines, current = [], ""
    for char in text:
        test = current + char
        if char == "\n":
            lines.append(current)
            current = ""
            continue
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines

def draw_text_block(draw, text, font, x, y, max_width, fill, line_gap=1.45):
    """绘制多行文字，返回末尾 y"""
    lines = wrap_text_pil(draw, text, font, max_width)
    bbox0 = draw.textbbox((0, 0), "测", font=font)
    lh = (bbox0[3] - bbox0[1]) * line_gap
    for line in lines:
        if line.strip():
            draw.text((x, y), line, font=font, fill=fill)
        y += lh
    return y

def draw_shadow_text(draw, text, font, x, y, fill, shadow_offset=3, shadow_alpha=120):
    """带阴影的文字"""
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, shadow_alpha))
    draw.text((x, y), text, font=font, fill=fill)

def draw_rounded_rect(draw, xy, r, fill=None, outline=None, width=2):
    x1, y1, x2, y2 = xy
    if fill:
        draw.rectangle([x1+r, y1, x2-r, y2], fill=fill)
        draw.rectangle([x1, y1+r, x2, y2-r], fill=fill)
        for cx, cy in [(x1, y1), (x2-2*r, y1), (x1, y2-2*r), (x2-2*r, y2-2*r)]:
            draw.ellipse([cx, cy, cx+2*r, cy+2*r], fill=fill)
    if outline:
        draw.arc([x1, y1, x1+2*r, y1+2*r], 180, 270, fill=outline, width=width)
        draw.arc([x2-2*r, y1, x2, y1+2*r], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2-2*r, x1+2*r, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2-2*r, y2-2*r, x2, y2], 0, 90, fill=outline, width=width)
        draw.line([x1+r, y1, x2-r, y1], fill=outline, width=width)
        draw.line([x1+r, y2, x2-r, y2], fill=outline, width=width)
        draw.line([x1, y1+r, x1, y2-r], fill=outline, width=width)
        draw.line([x2, y1+r, x2, y2-r], fill=outline, width=width)

def add_dark_overlay(img, alpha=140):
    """在图片上叠加半透明暗色层，提高文字可读性"""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, alpha))
    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")

def add_gradient_overlay(img, top_alpha=180, bottom_alpha=220):
    """渐变暗色叠加（上浅下深）"""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(img.height):
        t = y / img.height
        a = int(top_alpha * (1 - t) + bottom_alpha * t)
        draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, a))
    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")

# ── Gemini 图像生成 ───────────────────────────────────────

def generate_bg_with_gemini(prompt: str, card_key: str) -> Image.Image | None:
    """调用 Gemini 生成背景图，失败返回 None"""
    if not GEMINI_API_KEY:
        print(f"[WARN] No GEMINI_API_KEY, skipping bg generation for {card_key}")
        return None

    print(f"[INFO] Generating background for {card_key} via Gemini...")
    try:
        resp = requests.post(
            f"{GEMINI_IMG_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
            },
            timeout=90,
        )
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            print(f"[WARN] Gemini returned no candidates for {card_key}: {data.get('error', {}).get('message', '')}")
            return None
        for part in candidates[0].get("content", {}).get("parts", []):
            if "inlineData" in part:
                img_bytes = base64.b64decode(part["inlineData"]["data"])
                img = Image.open(BytesIO(img_bytes)).convert("RGB")
                # 调整到 1080×1350
                img = img.resize((W, H), Image.LANCZOS)
                print(f"[INFO] Background generated for {card_key}: {img.size}")
                return img
        print(f"[WARN] No image data in Gemini response for {card_key}")
        return None
    except Exception as e:
        print(f"[ERROR] Gemini generation failed for {card_key}: {e}")
        return None

def make_fallback_bg(color_top=(8, 15, 40), color_bottom=(20, 40, 90)) -> Image.Image:
    """Gemini 失败时的备用渐变背景"""
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(color_top[0]*(1-t) + color_bottom[0]*t)
        g = int(color_top[1]*(1-t) + color_bottom[1]*t)
        b = int(color_top[2]*(1-t) + color_bottom[2]*t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return img

# ── 卡片渲染 ──────────────────────────────────────────────

def render_cover(bg: Image.Image, content: dict, date_str: str, out_path: Path):
    """封面卡片"""
    # 叠加渐变暗色
    img = add_gradient_overlay(bg, top_alpha=100, bottom_alpha=200)
    draw = ImageDraw.Draw(img, "RGBA")

    cover = content["cover"]
    date_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y年%m月%d日")

    # 顶部彩虹条
    for i, c in enumerate(ACCENT_COLORS):
        draw.rectangle([i*(W//5), 0, (i+1)*(W//5), 8], fill=c)

    # 品牌 + 日期
    font_sm = load_font(FONT_REG, 30)
    draw.text((60, 55), "Awesome Harness Engineering", font=font_sm, fill=(*WHITE, 160))
    draw.text((W-280, 55), date_display, font=font_sm, fill=(*ACCENT_COLORS[0], 200))

    # 主标题（大字）
    font_title = load_font(FONT_BLACK, 76)
    headline = cover["headline"]
    y = 200
    lines = wrap_text_pil(draw, headline, font_title, W - 120)
    for line in lines:
        draw_shadow_text(draw, line, font_title, 60, y, WHITE, shadow_offset=4, shadow_alpha=150)
        bbox = draw.textbbox((0, 0), line, font=font_title)
        y += int((bbox[3] - bbox[1]) * 1.15)

    # 副标题
    font_sub = load_font(FONT_SERIF, 44)
    y += 20
    sub_lines = wrap_text_pil(draw, cover["subtitle"], font_sub, W - 120)
    for line in sub_lines:
        draw.text((60, y), line, font=font_sub, fill=(*WHITE, 200))
        bbox = draw.textbbox((0, 0), line, font=font_sub)
        y += int((bbox[3] - bbox[1]) * 1.3)

    # 分隔线
    y += 30
    draw.rectangle([60, y, 60+180, y+4], fill=ACCENT_COLORS[0])
    y += 40

    # 标签
    font_tag = load_font(FONT_BOLD, 30)
    tag_x = 60
    for i, tag in enumerate(cover["tags"][:4]):
        c = ACCENT_COLORS[i % 5]
        text = f"# {tag}"
        bbox = draw.textbbox((0, 0), text, font=font_tag)
        tw = bbox[2] - bbox[0] + 28
        if tag_x + tw > W - 60:
            break
        draw_rounded_rect(draw, [tag_x, y, tag_x+tw, y+52], 14, fill=(*c, 45))
        draw.text((tag_x+14, y+11), text, font=font_tag, fill=c)
        tag_x += tw + 16

    # 底部装饰条
    draw.rectangle([0, H-90, W, H-88], fill=(*ACCENT_COLORS[1], 120))
    font_footer = load_font(FONT_REG, 26)
    draw.text((60, H-68), "每日精选 · AI Agent Harness 工程实践", font=font_footer, fill=(*WHITE, 130))
    draw.text((W-80, H-68), "1/7", font=font_footer, fill=(*WHITE, 130))

    img.save(out_path, "PNG", quality=95)
    print(f"[OK] Cover saved → {out_path.name}")


def render_content_card(bg: Image.Image, card: dict, card_num: int, total: int, out_path: Path):
    """内容卡片（洞见 1-5）"""
    img = add_gradient_overlay(bg, top_alpha=80, bottom_alpha=210)
    draw = ImageDraw.Draw(img, "RGBA")

    idx = card["index"]
    color = ACCENT_COLORS[(idx - 1) % 5]

    # 左侧彩色竖条
    draw.rectangle([0, 0, 10, H], fill=(*color, 220))

    # 右上角大序号水印
    font_watermark = load_font(FONT_BLACK, 200)
    wm = f"0{idx}"
    draw.text((W - 200, -30), wm, font=font_watermark, fill=(*color, 20))

    # 序号圆标
    draw.ellipse([60, 60, 120, 120], fill=(*color, 220))
    font_idx = load_font(FONT_BLACK, 38)
    bbox = draw.textbbox((0, 0), str(idx), font=font_idx)
    cx = 60 + (60 - (bbox[2]-bbox[0])) // 2
    draw_shadow_text(draw, str(idx), font_idx, cx, 72, WHITE)

    # 标题
    font_title = load_font(FONT_BLACK, 64)
    y = 170
    title_lines = wrap_text_pil(draw, card["title"], font_title, W - 130)
    for line in title_lines:
        draw_shadow_text(draw, line, font_title, 60, y, WHITE, shadow_offset=3)
        bbox = draw.textbbox((0, 0), line, font=font_title)
        y += int((bbox[3] - bbox[1]) * 1.15)

    # 标题下划线
    y += 12
    draw.rectangle([60, y, 60+220, y+5], fill=(*color, 200))
    y += 32

    # 正文
    font_body = load_font(FONT_SERIF, 38)
    body = card.get("body", "")
    # 添加半透明背景提升可读性
    body_lines = wrap_text_pil(draw, body, font_body, W - 120)
    bbox0 = draw.textbbox((0, 0), "测", font=font_body)
    lh = (bbox0[3] - bbox0[1]) * 1.5
    body_h = len(body_lines) * lh + 30
    draw_rounded_rect(draw, [50, y-10, W-50, y+body_h], 12, fill=(0, 0, 0, 100))
    y = draw_text_block(draw, body, font_body, 70, y+5, W - 140, WHITE90, line_gap=1.5)
    y += 25

    # 金句卡片
    quote = card.get("quote", "")
    if quote:
        qh = 130
        draw_rounded_rect(draw, [60, y, W-60, y+qh], 16,
                          fill=(*color, 35), outline=(*color, 120), width=2)
        font_q_mark = load_font(FONT_BLACK, 52)
        draw.text((78, y+8), "❝", font=font_q_mark, fill=(*color, 180))
        font_quote = load_font(FONT_SERIF_B, 36)
        draw_text_block(draw, quote, font_quote, 130, y+18, W - 200, color, line_gap=1.4)
        y += qh + 20

    # 来源
    source = card.get("source", "")
    if source:
        font_src = load_font(FONT_REG, 28)
        src_text = f"📌  {source}"
        draw_rounded_rect(draw, [60, y, 60+len(source)*20+80, y+46], 12,
                          fill=(0, 0, 0, 100))
        draw.text((80, y+9), src_text, font=font_src, fill=(*WHITE, 160))

    # 底部
    draw.rectangle([0, H-85, W, H-83], fill=(*color, 80))
    font_footer = load_font(FONT_REG, 26)
    draw.text((60, H-65), "Awesome Harness Engineering", font=font_footer, fill=(*WHITE, 120))
    draw.text((W-90, H-65), f"{card_num}/7", font=font_footer, fill=(*WHITE, 120))

    img.save(out_path, "PNG", quality=95)
    print(f"[OK] Card {idx} saved → {out_path.name}")


def render_summary(bg: Image.Image, content: dict, articles: list, date_str: str, out_path: Path):
    """总结卡片"""
    img = add_gradient_overlay(bg, top_alpha=90, bottom_alpha=200)
    draw = ImageDraw.Draw(img, "RGBA")

    summary = content.get("summary", {})

    # 顶部彩虹条
    for i, c in enumerate(ACCENT_COLORS):
        draw.rectangle([i*(W//5), 0, (i+1)*(W//5), 8], fill=c)

    # 标题
    font_title = load_font(FONT_BLACK, 60)
    title = summary.get("title", "今日要点回顾")
    draw_shadow_text(draw, title, font_title, 60, 55, WHITE)

    # 分隔线
    draw.rectangle([60, 140, W-60, 144], fill=(*ACCENT_COLORS[0], 100))

    # 要点列表
    font_point = load_font(FONT_BOLD, 40)
    points = summary.get("points", [])
    y = 175
    for i, point in enumerate(points[:4]):
        c = ACCENT_COLORS[i % 5]
        # 序号圆
        draw.ellipse([60, y+2, 104, y+46], fill=(*c, 200))
        font_num = load_font(FONT_BLACK, 28)
        bbox = draw.textbbox((0, 0), str(i+1), font=font_num)
        cx = 60 + (44 - (bbox[2]-bbox[0])) // 2
        draw.text((cx, y+9), str(i+1), font=font_num, fill=WHITE)
        # 文字
        draw.text((120, y+5), point, font=font_point, fill=WHITE90)
        y += 72

    y += 15
    draw.rectangle([60, y, W-60, y+2], fill=(*ACCENT_COLORS[1], 60))
    y += 30

    # 统计数字
    stats = [
        (str(len(articles)), "今日新增资源"),
        (str(sum(1 for a in articles if a.get("quality_score", 0) >= 8)), "高质量精选"),
        (date_str.replace("-", "/"), "更新日期"),
    ]
    font_stat_big = load_font(FONT_BLACK, 44)
    font_stat_sm  = load_font(FONT_REG, 30)
    sw = (W - 120) // 3
    for i, (val, label) in enumerate(stats):
        sx = 60 + i * sw
        c = ACCENT_COLORS[i % 5]
        draw_rounded_rect(draw, [sx, y, sx+sw-20, y+130], 16,
                          fill=(*c, 25), outline=(*c, 80), width=2)
        bbox = draw.textbbox((0, 0), val, font=font_stat_big)
        vw = bbox[2] - bbox[0]
        draw.text((sx + (sw-20-vw)//2, y+15), val, font=font_stat_big, fill=c)
        bbox2 = draw.textbbox((0, 0), label, font=font_stat_sm)
        lw = bbox2[2] - bbox2[0]
        draw.text((sx + (sw-20-lw)//2, y+72), label, font=font_stat_sm, fill=(*WHITE, 160))
    y += 155

    # CTA 框
    cta = summary.get("cta", "关注我，每天追踪 Harness Engineering 最新动态")
    font_cta = load_font(FONT_SERIF_B, 38)
    cta_lines = wrap_text_pil(draw, cta, font_cta, W - 180)
    bbox0 = draw.textbbox((0, 0), "测", font=font_cta)
    cta_h = len(cta_lines) * (bbox0[3]-bbox0[1]) * 1.4 + 40
    draw_rounded_rect(draw, [60, y, W-60, y+cta_h], 20,
                      fill=(*ACCENT_COLORS[0], 30), outline=(*ACCENT_COLORS[0], 120), width=2)
    draw_text_block(draw, cta, font_cta, 90, y+20, W-180, ACCENT_COLORS[0], line_gap=1.4)
    y += cta_h + 20

    # Hashtags
    font_ht = load_font(FONT_REG, 28)
    ht_x, ht_y = 60, y + 10
    for i, tag in enumerate(summary.get("hashtags", [])[:6]):
        c = ACCENT_COLORS[i % 5]
        bbox = draw.textbbox((0, 0), tag, font=font_ht)
        tw = bbox[2] - bbox[0] + 24
        if ht_x + tw > W - 60:
            ht_x = 60
            ht_y += 48
        draw_rounded_rect(draw, [ht_x, ht_y, ht_x+tw, ht_y+40], 10, fill=(*c, 35))
        draw.text((ht_x+12, ht_y+6), tag, font=font_ht, fill=c)
        ht_x += tw + 14

    # 底部
    draw.rectangle([0, H-85, W, H-83], fill=(*ACCENT_COLORS[1], 80))
    font_footer = load_font(FONT_REG, 26)
    draw.text((60, H-65), "github.com/liuestc/awesome-harness-engineering",
              font=font_footer, fill=(*WHITE, 120))
    draw.text((W-80, H-65), "7/7", font=font_footer, fill=(*WHITE, 120))

    img.save(out_path, "PNG", quality=95)
    print(f"[OK] Summary saved → {out_path.name}")

# ── MiniMax 内容提炼 ──────────────────────────────────────

def call_minimax(prompt: str) -> str:
    if not MINIMAX_API_KEY:
        return ""
    try:
        resp = requests.post(
            MINIMAX_API_URL,
            headers={"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"},
            json={"model": MINIMAX_MODEL, "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 8192, "temperature": 0.7},
            timeout=120,
        )
        choices = resp.json().get("choices")
        return choices[0]["message"]["content"] if choices else ""
    except Exception as e:
        print(f"[ERROR] MiniMax: {e}")
        return ""

def extract_digest_content(articles: list, date_str: str) -> dict:
    articles_text = ""
    for i, a in enumerate(articles[:10], 1):
        title = a.get("title_zh") or a.get("title_en") or ""
        summary = a.get("ai_summary_zh") or a.get("ai_summary_en") or ""
        insights = "; ".join(a.get("key_concepts", [])[:3])
        score = a.get("quality_score", 0)
        articles_text += f"\n{i}. 【{title}】(评分:{score})\n   摘要: {summary[:150]}\n   关键概念: {insights}\n"

    prompt = f"""你是一位专注 AI 工程领域的技术博主，擅长把复杂技术转化为易懂的小红书图文。

今天是 {date_str}，以下是今日收集到的 Harness Engineering 相关资源：
{articles_text}

请生成一套小红书图文脚本，严格按以下 JSON 格式输出，不要有任何其他文字：

{{
  "cover": {{
    "headline": "封面大标题（15字以内，要有冲击力，可以用数字/符号）",
    "subtitle": "副标题（20字以内，补充说明）",
    "tags": ["标签1", "标签2", "标签3", "标签4"]
  }},
  "cards": [
    {{"index": 1, "title": "卡片标题（10字以内）", "body": "正文（80-120字，中英混排，技术术语保留英文）", "quote": "金句（30字以内）", "source": "来源简称"}},
    {{"index": 2, "title": "...", "body": "...", "quote": "...", "source": "..."}},
    {{"index": 3, "title": "...", "body": "...", "quote": "...", "source": "..."}},
    {{"index": 4, "title": "...", "body": "...", "quote": "...", "source": "..."}},
    {{"index": 5, "title": "...", "body": "...", "quote": "...", "source": "..."}}
  ],
  "summary": {{
    "title": "今日总结标题",
    "points": ["要点1（15字以内）", "要点2", "要点3", "要点4"],
    "cta": "行动号召语（25字以内）",
    "hashtags": ["#HarnessEngineering", "#AI工程师", "#Claude", "#AgentDev", "#技术前沿", "#LLM应用"]
  }}
}}"""

    print("[INFO] Calling MiniMax-M2.7 to extract digest content...")
    raw = call_minimax(prompt)
    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        try:
            return json.loads(match.group())
        except Exception as e:
            print(f"[WARN] JSON parse error: {e}")
    print("[WARN] Using fallback content")
    return _fallback_content(articles, date_str)

def _fallback_content(articles, date_str):
    titles = [a.get("title_zh") or a.get("title_en", "") for a in articles[:5]]
    return {
        "cover": {"headline": "今日 Harness Engineering 精选", "subtitle": f"{date_str} · {len(articles)} 篇优质资源", "tags": ["HarnessEngineering", "AI Agent", "工程实践", "LLM"]},
        "cards": [{"index": i+1, "title": titles[i][:20] if i < len(titles) else f"洞见 {i+1}", "body": articles[i].get("ai_summary_zh", "") if i < len(articles) else "", "quote": "", "source": "今日精选"} for i in range(min(5, len(articles)))],
        "summary": {"title": "今日要点回顾", "points": [a.get("title_zh", "")[:20] for a in articles[:4]], "cta": "关注我，追踪 Harness Engineering 最新动态", "hashtags": ["#HarnessEngineering", "#AI工程师", "#AgentDev"]}
    }

# ── 主流程 ────────────────────────────────────────────────

def main():
    tz_bj = timezone(timedelta(hours=8))
    today = datetime.now(tz_bj).strftime("%Y-%m-%d")
    date_arg = sys.argv[1] if len(sys.argv) > 1 else today

    print(f"\n{'='*60}")
    print(f"Daily Digest Generator v2 (Gemini BG) — {date_arg}")
    print(f"{'='*60}")

    # 读取文章
    articles_path = DATA_DIR / "articles.json"
    if not articles_path.exists():
        print("[ERROR] articles.json not found"); sys.exit(1)
    with open(articles_path) as f:
        all_articles = json.load(f)

    today_articles = [a for a in all_articles if a.get("discovered_at", "").startswith(date_arg)]
    if not today_articles:
        print(f"[INFO] No articles for {date_arg}, using latest high-quality articles")
        today_articles = sorted(
            [a for a in all_articles if a.get("quality_score", 0) >= 7.5],
            key=lambda x: x.get("discovered_at", ""), reverse=True
        )[:8]
    print(f"[INFO] Processing {len(today_articles)} articles")

    # 输出目录
    out_dir = DIGEST_DIR / date_arg
    out_dir.mkdir(parents=True, exist_ok=True)

    # 读取或生成 digest 内容
    digest_json_path = out_dir / "digest.json"
    if digest_json_path.exists():
        with open(digest_json_path) as f:
            saved = json.load(f)
        digest_content = saved.get("content")
        print("[INFO] Loaded existing digest.json")
    else:
        digest_content = extract_digest_content(today_articles, date_arg)

    # 保存 JSON
    with open(digest_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_arg,
            "generated_at": datetime.now(tz_bj).isoformat(),
            "article_count": len(today_articles),
            "content": digest_content,
            "source_articles": [{"title": a.get("title_zh") or a.get("title_en"), "url": a.get("url"), "score": a.get("quality_score")} for a in today_articles[:10]]
        }, f, ensure_ascii=False, indent=2)

    cards_data = digest_content.get("cards", [])

    # ── 生成所有背景图（并行请求会触发限速，改为顺序+间隔）──
    print("\n[INFO] Generating backgrounds with Gemini...")

    bg_cover   = generate_bg_with_gemini(BG_PROMPTS["cover"],     "cover")   or make_fallback_bg()
    time.sleep(2)
    bg_cards   = []
    for i in range(5):
        key = f"insight_{i+1}"
        bg = generate_bg_with_gemini(BG_PROMPTS[key], key) or make_fallback_bg()
        bg_cards.append(bg)
        time.sleep(2)
    bg_summary = generate_bg_with_gemini(BG_PROMPTS["summary"], "summary") or make_fallback_bg()

    # ── 渲染卡片 ──
    print("\n[INFO] Rendering cards...")
    render_cover(bg_cover, digest_content, date_arg, out_dir / "card_00_cover.png")
    for i, card in enumerate(cards_data[:5]):
        render_content_card(bg_cards[i], card, i+2, 7, out_dir / f"card_0{i+1}_{card['index']}.png")
    render_summary(bg_summary, digest_content, today_articles, date_arg, out_dir / "card_07_summary.png")

    # 更新 meta.json
    meta_path = DATA_DIR / "meta.json"
    meta = json.load(open(meta_path)) if meta_path.exists() else {}
    if "daily_digests" not in meta:
        meta["daily_digests"] = []
    entry = {
        "date": date_arg,
        "article_count": len(today_articles),
        "headline": digest_content.get("cover", {}).get("headline", ""),
        "cards": ["card_00_cover.png"] + [f"card_0{i+1}_{c['index']}.png" for i, c in enumerate(cards_data[:5])] + ["card_07_summary.png"]
    }
    meta["daily_digests"] = [e for e in meta["daily_digests"] if e["date"] != date_arg]
    meta["daily_digests"].insert(0, entry)
    meta["daily_digests"] = meta["daily_digests"][:30]
    meta["last_digest_date"] = date_arg
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    pngs = list(out_dir.glob("*.png"))
    print(f"\n✅ Done! {len(pngs)} cards → {out_dir}")

if __name__ == "__main__":
    main()
