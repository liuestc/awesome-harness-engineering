/**
 * 模板 C：「杂志专栏」Editorial Magazine
 * 设计语言：高端科技杂志风格，类似 MIT Technology Review
 * 深蓝灰底 + 米白色正文 + 大号序号 + 衬线标题 + 渐进章节色
 */

// 每张卡片有不同的章节色，整套图文色彩渐进
const CHAPTER_COLORS = [
  { bg: '#0f1923', accent: '#e8d5b7', text: '#f5f0e8', sub: '#a89880' },   // 封面：暖金
  { bg: '#0d1f2d', accent: '#7eb8d4', text: '#e8f4f8', sub: '#6a9ab0' },   // 1：冰蓝
  { bg: '#1a1a2e', accent: '#c084fc', text: '#f0e8ff', sub: '#9b6cc7' },   // 2：紫罗兰
  { bg: '#0f2318', accent: '#6ee7b7', text: '#e8fff4', sub: '#4db88a' },   // 3：翡翠绿
  { bg: '#2d1a0f', accent: '#fb923c', text: '#fff4e8', sub: '#c07040' },   // 4：琥珀橙
  { bg: '#1f0d1f', accent: '#f472b6', text: '#ffe8f4', sub: '#c05090' },   // 5：玫瑰红
  { bg: '#0a1628', accent: '#60a5fa', text: '#e8f0ff', sub: '#4070c0' },   // 总结：深蓝
];

function coverC(data) {
  const { headline, subtitle, tags, date } = data;
  const c = CHAPTER_COLORS[0];
  const tagHtml = (tags || []).slice(0,4).map(t =>
    `<span class="tag">${t}</span>`).join('');

  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:${c.bg};font-family:'Noto Sans SC',sans-serif;overflow:hidden;position:relative}
.texture{position:absolute;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E");opacity:.5}
.top-rule{position:absolute;top:0;left:0;right:0;height:6px;background:${c.accent}}
.bottom-rule{position:absolute;bottom:0;left:0;right:0;height:3px;background:${c.accent};opacity:.4}
.side-margin{position:absolute;top:0;left:80px;bottom:0;width:1px;background:${c.accent};opacity:.15}
.content{position:relative;z-index:10;padding:70px 80px 60px 100px;height:100%;display:flex;flex-direction:column}
.vol-line{display:flex;justify-content:space-between;align-items:center;margin-bottom:60px;padding-bottom:20px;border-bottom:1px solid ${c.accent}44}
.vol{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.sub};letter-spacing:.2em;text-transform:uppercase}
.date-text{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.sub};letter-spacing:.1em}
.kicker{font-family:'Noto Sans SC',sans-serif;font-size:22px;color:${c.accent};letter-spacing:.25em;text-transform:uppercase;margin-bottom:28px;font-weight:600}
.headline{font-family:'Noto Serif SC',serif;font-size:86px;font-weight:700;line-height:1.08;color:${c.text};margin-bottom:36px;letter-spacing:-.01em}
.headline em{font-style:italic;color:${c.accent}}
.rule{width:100%;height:1px;background:${c.accent}55;margin-bottom:32px}
.subtitle{font-family:'Noto Serif SC',serif;font-size:36px;color:${c.sub};line-height:1.7;margin-bottom:56px;font-weight:400}
.tags{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:auto}
.tag{font-family:'Noto Sans SC',sans-serif;font-size:20px;color:${c.sub};padding:8px 20px;border:1px solid ${c.accent}44;letter-spacing:.08em}
.footer{display:flex;justify-content:space-between;align-items:flex-end;padding-top:28px;border-top:1px solid ${c.accent}33}
.footer-brand{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.sub};letter-spacing:.1em}
.page-num{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.sub}}
</style></head><body>
<div class="texture"></div>
<div class="top-rule"></div>
<div class="bottom-rule"></div>
<div class="side-margin"></div>
<div class="content">
  <div class="vol-line">
    <span class="vol">Awesome Harness Engineering</span>
    <span class="date-text">${date}</span>
  </div>
  <div class="kicker">今日精选 · Daily Digest</div>
  <div class="headline">${headline.replace(/(Harness|Agent|AI)/g,'<em>$1</em>')}</div>
  <div class="rule"></div>
  <div class="subtitle">${subtitle}</div>
  <div class="tags">${tagHtml}</div>
  <div class="footer">
    <span class="footer-brand">每日精选 · AI Agent 工程实践</span>
    <span class="page-num">1 / 7</span>
  </div>
</div>
</body></html>`;
}

function contentCardC(card, cardNum) {
  const { index, title, body, quote, source } = card;
  const c = CHAPTER_COLORS[index] || CHAPTER_COLORS[1];

  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:${c.bg};font-family:'Noto Sans SC',sans-serif;overflow:hidden;position:relative}
.texture{position:absolute;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E");opacity:.5}
.top-rule{position:absolute;top:0;left:0;right:0;height:5px;background:${c.accent}}
.big-num{position:absolute;top:40px;right:60px;font-family:'Playfair Display',serif;font-size:280px;font-weight:900;color:${c.accent};opacity:.07;line-height:1;letter-spacing:-.05em}
.side-accent{position:absolute;top:0;left:0;bottom:0;width:6px;background:${c.accent}}
.content{position:relative;z-index:10;padding:70px 80px 60px 100px;height:100%;display:flex;flex-direction:column}
.chapter-row{display:flex;align-items:center;gap:20px;margin-bottom:48px}
.chapter-badge{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.bg};background:${c.accent};padding:8px 20px;letter-spacing:.15em;font-weight:600}
.chapter-label{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.sub};letter-spacing:.2em;text-transform:uppercase}
.title{font-family:'Noto Serif SC',serif;font-size:72px;font-weight:700;color:${c.text};line-height:1.1;margin-bottom:20px;letter-spacing:-.01em}
.title-rule{width:80px;height:3px;background:${c.accent};margin-bottom:44px}
.body{font-family:'Noto Serif SC',serif;font-size:36px;color:${c.sub};line-height:1.85;margin-bottom:44px;flex:1;font-weight:400}
.quote-box{border-left:4px solid ${c.accent};padding:24px 36px;margin-bottom:28px;background:${c.accent}0d}
.quote-text{font-family:'Noto Serif SC',serif;font-size:34px;font-weight:600;color:${c.accent};line-height:1.55;font-style:italic}
.source-row{display:flex;align-items:center;gap:12px}
.source-dash{width:24px;height:1px;background:${c.sub}}
.source-text{font-family:'Noto Sans SC',sans-serif;font-size:20px;color:${c.sub};letter-spacing:.05em}
.footer{display:flex;justify-content:space-between;align-items:center;padding-top:28px;border-top:1px solid ${c.accent}33}
.footer-brand{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.sub};letter-spacing:.08em}
.page-num{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.sub}}
</style></head><body>
<div class="texture"></div>
<div class="top-rule"></div>
<div class="big-num">${index}</div>
<div class="side-accent"></div>
<div class="content">
  <div class="chapter-row">
    <span class="chapter-badge">洞见 ${index}</span>
    <span class="chapter-label">Insight · ${String(index).padStart(2,'0')}</span>
  </div>
  <div class="title">${title}</div>
  <div class="title-rule"></div>
  <div class="body">${body}</div>
  ${quote ? `<div class="quote-box"><div class="quote-text">${quote}</div></div>` : ''}
  ${source ? `<div class="source-row"><div class="source-dash"></div><span class="source-text">via ${source}</span></div>` : ''}
  <div class="footer">
    <span class="footer-brand">Awesome Harness Engineering</span>
    <span class="page-num">${cardNum} / 7</span>
  </div>
</div>
</body></html>`;
}

function summaryC(summary, articles, date) {
  const c = CHAPTER_COLORS[6];
  const points = (summary.points || []).slice(0,4);
  const pointsHtml = points.map((p,i) => {
    const pc = CHAPTER_COLORS[i+1];
    return `<div class="point">
      <span class="point-num" style="background:${pc.accent};color:${pc.bg}">${String(i+1).padStart(2,'0')}</span>
      <span class="point-text">${p}</span>
    </div>`;
  }).join('');
  const tags = (summary.hashtags || []).slice(0,6).map(t =>
    `<span class="htag">${t}</span>`).join('');

  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:${c.bg};font-family:'Noto Sans SC',sans-serif;overflow:hidden;position:relative}
.texture{position:absolute;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E");opacity:.5}
.rainbow-rule{position:absolute;top:0;left:0;right:0;height:6px;background:linear-gradient(90deg,#e8d5b7,#7eb8d4,#c084fc,#6ee7b7,#fb923c,#f472b6,#60a5fa)}
.content{position:relative;z-index:10;padding:70px 80px 60px 80px;height:100%;display:flex;flex-direction:column}
.title{font-family:'Noto Serif SC',serif;font-size:64px;font-weight:700;color:${c.text};margin-bottom:12px;letter-spacing:-.01em}
.subtitle{font-family:'Noto Sans SC',sans-serif;font-size:20px;color:${c.sub};margin-bottom:44px;letter-spacing:.15em;text-transform:uppercase}
.rule{width:100%;height:1px;background:${c.accent}44;margin-bottom:36px}
.points{display:flex;flex-direction:column;gap:22px;margin-bottom:36px}
.point{display:flex;align-items:center;gap:24px}
.point-num{font-family:'Noto Sans SC',sans-serif;font-size:22px;font-weight:700;width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex-shrink:0;letter-spacing:.05em}
.point-text{font-family:'Noto Serif SC',serif;font-size:36px;font-weight:600;color:${c.text}}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:36px}
.stat{border:1px solid ${c.accent}33;padding:20px;text-align:center;background:${c.accent}08}
.stat-val{font-family:'Noto Sans SC',sans-serif;font-size:48px;font-weight:700;color:${c.accent};display:block}
.stat-label{font-family:'Noto Sans SC',sans-serif;font-size:20px;color:${c.sub};margin-top:6px}
.cta{border-left:4px solid ${c.accent};padding:20px 28px;background:${c.accent}0d;margin-bottom:28px}
.cta-text{font-family:'Noto Serif SC',serif;font-size:32px;color:${c.accent};font-weight:600;font-style:italic}
.htags{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:auto}
.htag{font-family:'Noto Sans SC',sans-serif;font-size:20px;color:${c.sub};padding:6px 16px;border:1px solid ${c.accent}33}
.footer{display:flex;justify-content:space-between;padding-top:24px;border-top:1px solid ${c.accent}33}
.footer-url{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.sub}}
.page-num{font-family:'Noto Sans SC',sans-serif;font-size:18px;color:${c.sub}}
</style></head><body>
<div class="texture"></div>
<div class="rainbow-rule"></div>
<div class="content">
  <div class="title">${summary.title || '今日要点回顾'}</div>
  <div class="subtitle">Daily Summary · ${date}</div>
  <div class="rule"></div>
  <div class="points">${pointsHtml}</div>
  <div class="stats">
    <div class="stat"><span class="stat-val">${articles.length}</span><div class="stat-label">今日资源</div></div>
    <div class="stat"><span class="stat-val">${articles.filter(a=>(a.quality_score||0)>=8).length}</span><div class="stat-label">高质量精选</div></div>
    <div class="stat"><span class="stat-val">${date.replace(/-/g,'/')}</span><div class="stat-label">更新日期</div></div>
  </div>
  <div class="cta"><div class="cta-text">${summary.cta || '关注我，追踪 Harness Engineering 最新动态'}</div></div>
  <div class="htags">${tags}</div>
  <div class="footer">
    <span class="footer-url">github.com/liuestc/awesome-harness-engineering</span>
    <span class="page-num">7 / 7</span>
  </div>
</div>
</body></html>`;
}

module.exports = { coverC, contentCardC, summaryC };
