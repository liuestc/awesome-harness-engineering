/**
 * 模板 A：「极简技术派」Minimal Tech
 * 设计语言：克制、高级感，类似 Linear / Vercel 风格
 * 纯黑底 + 白色大字 + 单色强调 + 大量留白
 */

const ACCENT = '#3b82f6'; // 电蓝
const ACCENTS = ['#3b82f6','#10b981','#f59e0b','#8b5cf6','#ef4444'];

function coverA(data) {
  const { headline, subtitle, tags, date } = data;
  const tagHtml = (tags || []).slice(0,4).map((t,i) =>
    `<span class="tag" style="border-color:${ACCENTS[i%5]};color:${ACCENTS[i%5]}"># ${t}</span>`
  ).join('');

  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+SC:wght@300;400;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#050505;font-family:'Noto Sans SC',sans-serif;overflow:hidden;position:relative}
.noise{position:absolute;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");opacity:.4}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(59,130,246,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,.04) 1px,transparent 1px);background-size:60px 60px}
.accent-bar{position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#3b82f6,#8b5cf6,#10b981)}
.side-bar{position:absolute;top:0;left:0;bottom:0;width:4px;background:linear-gradient(180deg,#3b82f6 0%,#8b5cf6 50%,#10b981 100%)}
.content{position:relative;z-index:10;padding:80px 80px 60px 100px;height:100%;display:flex;flex-direction:column}
.brand{font-family:'JetBrains Mono',monospace;font-size:22px;color:rgba(255,255,255,.3);letter-spacing:.1em;margin-bottom:auto}
.date-badge{font-family:'JetBrains Mono',monospace;font-size:20px;color:rgba(59,130,246,.7);letter-spacing:.05em}
.top-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:120px}
.headline{font-size:88px;font-weight:900;line-height:1.05;color:#fff;letter-spacing:-.02em;margin-bottom:32px;text-shadow:0 0 80px rgba(59,130,246,.15)}
.headline em{font-style:normal;color:#3b82f6}
.subtitle{font-size:36px;font-weight:300;color:rgba(255,255,255,.5);line-height:1.5;margin-bottom:60px;max-width:800px}
.divider{width:120px;height:2px;background:#3b82f6;margin-bottom:48px}
.tags{display:flex;flex-wrap:wrap;gap:16px}
.tag{font-family:'JetBrains Mono',monospace;font-size:24px;padding:10px 22px;border:1px solid;border-radius:4px;letter-spacing:.05em}
.footer{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end}
.footer-brand{font-family:'JetBrains Mono',monospace;font-size:20px;color:rgba(255,255,255,.2)}
.page-num{font-family:'JetBrains Mono',monospace;font-size:20px;color:rgba(255,255,255,.2)}
</style></head><body>
<div class="noise"></div>
<div class="grid"></div>
<div class="accent-bar"></div>
<div class="side-bar"></div>
<div class="content">
  <div class="top-row">
    <span class="brand">Awesome Harness Engineering</span>
    <span class="date-badge">${date}</span>
  </div>
  <div class="headline">${headline.replace(/(Harness|Agent|AI)/g,'<em>$1</em>')}</div>
  <div class="subtitle">${subtitle}</div>
  <div class="divider"></div>
  <div class="tags">${tagHtml}</div>
  <div class="footer">
    <span class="footer-brand">每日精选 · AI Agent 工程实践</span>
    <span class="page-num">1 / 7</span>
  </div>
</div>
</body></html>`;
}

function contentCardA(card, cardNum) {
  const { index, title, body, quote, source } = card;
  const color = ACCENTS[(index-1) % 5];
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+SC:wght@300;400;700;900&family=Noto+Serif+SC:wght@400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#050505;font-family:'Noto Sans SC',sans-serif;overflow:hidden;position:relative}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:60px 60px}
.side-bar{position:absolute;top:0;left:0;bottom:0;width:4px;background:${color}}
.glow{position:absolute;top:-200px;right:-200px;width:600px;height:600px;background:radial-gradient(circle,${color}18 0%,transparent 70%);pointer-events:none}
.content{position:relative;z-index:10;padding:80px 80px 60px 100px;height:100%;display:flex;flex-direction:column}
.index-row{display:flex;align-items:center;gap:24px;margin-bottom:56px}
.index-num{font-family:'JetBrains Mono',monospace;font-size:100px;font-weight:700;color:${color};opacity:.15;line-height:1;position:absolute;top:60px;right:80px}
.index-badge{width:56px;height:56px;border-radius:50%;background:${color};display:flex;align-items:center;justify-content:center;font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:700;color:#050505}
.index-label{font-family:'JetBrains Mono',monospace;font-size:22px;color:rgba(255,255,255,.3);letter-spacing:.1em}
.title{font-size:72px;font-weight:900;color:#fff;line-height:1.1;margin-bottom:24px;letter-spacing:-.02em}
.title-line{width:80px;height:3px;background:${color};margin-bottom:48px}
.body{font-family:'Noto Serif SC',serif;font-size:36px;color:rgba(255,255,255,.75);line-height:1.8;margin-bottom:48px;flex:1}
.quote-box{border-left:3px solid ${color};padding:24px 32px;background:${color}10;margin-bottom:32px}
.quote-text{font-size:34px;font-weight:700;color:${color};line-height:1.5}
.source-row{display:flex;align-items:center;gap:12px}
.source-dot{width:8px;height:8px;border-radius:50%;background:${color}}
.source-text{font-family:'JetBrains Mono',monospace;font-size:22px;color:rgba(255,255,255,.3)}
.footer{display:flex;justify-content:space-between;align-items:center;padding-top:32px;border-top:1px solid rgba(255,255,255,.06)}
.footer-brand{font-family:'JetBrains Mono',monospace;font-size:20px;color:rgba(255,255,255,.2)}
.page-num{font-family:'JetBrains Mono',monospace;font-size:20px;color:rgba(255,255,255,.2)}
</style></head><body>
<div class="grid"></div>
<div class="side-bar"></div>
<div class="glow"></div>
<div class="content">
  <div class="index-num">0${index}</div>
  <div class="index-row">
    <div class="index-badge">${index}</div>
    <span class="index-label">INSIGHT · ${String(index).padStart(2,'0')}</span>
  </div>
  <div class="title">${title}</div>
  <div class="title-line"></div>
  <div class="body">${body}</div>
  ${quote ? `<div class="quote-box"><div class="quote-text">${quote}</div></div>` : ''}
  ${source ? `<div class="source-row"><div class="source-dot"></div><span class="source-text">via ${source}</span></div>` : ''}
  <div class="footer">
    <span class="footer-brand">Awesome Harness Engineering</span>
    <span class="page-num">${cardNum} / 7</span>
  </div>
</div>
</body></html>`;
}

function summaryA(summary, articles, date) {
  const points = (summary.points || []).slice(0,4);
  const pointsHtml = points.map((p,i) => `
    <div class="point">
      <span class="point-num" style="color:${ACCENTS[i%5]};border-color:${ACCENTS[i%5]}">${String(i+1).padStart(2,'0')}</span>
      <span class="point-text">${p}</span>
    </div>`).join('');
  const tags = (summary.hashtags || []).slice(0,6).map((t,i) =>
    `<span class="htag" style="color:${ACCENTS[i%5]}">${t}</span>`).join('');

  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+SC:wght@300;400;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#050505;font-family:'Noto Sans SC',sans-serif;overflow:hidden;position:relative}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:60px 60px}
.rainbow-bar{position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#3b82f6,#8b5cf6,#10b981,#f59e0b,#ef4444)}
.content{position:relative;z-index:10;padding:80px 80px 60px 80px;height:100%;display:flex;flex-direction:column}
.title{font-size:68px;font-weight:900;color:#fff;margin-bottom:16px;letter-spacing:-.02em}
.subtitle{font-family:'JetBrains Mono',monospace;font-size:22px;color:rgba(255,255,255,.3);margin-bottom:60px;letter-spacing:.05em}
.divider{width:100%;height:1px;background:rgba(255,255,255,.08);margin-bottom:48px}
.points{display:flex;flex-direction:column;gap:28px;margin-bottom:48px}
.point{display:flex;align-items:center;gap:28px}
.point-num{font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:700;width:64px;height:64px;border:2px solid;border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.point-text{font-size:38px;font-weight:700;color:rgba(255,255,255,.85)}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:48px}
.stat{border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:24px;text-align:center}
.stat-val{font-family:'JetBrains Mono',monospace;font-size:52px;font-weight:700;color:#3b82f6;display:block}
.stat-label{font-size:22px;color:rgba(255,255,255,.3);margin-top:8px}
.cta{border:1px solid rgba(59,130,246,.3);border-radius:8px;padding:28px 36px;background:rgba(59,130,246,.05);margin-bottom:36px}
.cta-text{font-size:34px;color:#3b82f6;font-weight:600}
.htags{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:auto}
.htag{font-family:'JetBrains Mono',monospace;font-size:22px;opacity:.7}
.footer{display:flex;justify-content:space-between;padding-top:28px;border-top:1px solid rgba(255,255,255,.06)}
.footer-url{font-family:'JetBrains Mono',monospace;font-size:20px;color:rgba(255,255,255,.2)}
.page-num{font-family:'JetBrains Mono',monospace;font-size:20px;color:rgba(255,255,255,.2)}
</style></head><body>
<div class="grid"></div>
<div class="rainbow-bar"></div>
<div class="content">
  <div class="title">${summary.title || '今日要点回顾'}</div>
  <div class="subtitle">DAILY SUMMARY · ${date}</div>
  <div class="divider"></div>
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

module.exports = { coverA, contentCardA, summaryA };
