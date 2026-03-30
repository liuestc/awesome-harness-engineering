/**
 * 模板 B：「赛博霓虹」Cyberpunk Neon
 * 设计语言：暗黑科技感，霓虹灯效果，强烈视觉冲击
 * 深黑底 + 霓虹渐变文字 + 发光效果 + 网格纹理
 */

const NEON_PAIRS = [
  ['#00f5ff','#bf00ff'],
  ['#00ff88','#00bfff'],
  ['#ff6b35','#ff00aa'],
  ['#ffdd00','#ff6b35'],
  ['#00f5ff','#00ff88'],
];

function coverB(data) {
  const { headline, subtitle, tags, date } = data;
  const tagHtml = (tags || []).slice(0,4).map((t,i) => {
    const [c1,c2] = NEON_PAIRS[i%5];
    return `<span class="tag" style="border-color:${c1};color:${c1};box-shadow:0 0 12px ${c1}44"># ${t}</span>`;
  }).join('');

  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Noto+Sans+SC:wght@300;400;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#020010;font-family:'Noto Sans SC',sans-serif;overflow:hidden;position:relative}
.scanlines{position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,245,255,.015) 2px,rgba(0,245,255,.015) 4px);pointer-events:none;z-index:1}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(0,245,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(0,245,255,.06) 1px,transparent 1px);background-size:54px 54px;z-index:0}
.glow-top{position:absolute;top:-300px;left:50%;transform:translateX(-50%);width:1200px;height:600px;background:radial-gradient(ellipse,rgba(191,0,255,.2) 0%,transparent 70%)}
.glow-bottom{position:absolute;bottom:-200px;right:-100px;width:800px;height:600px;background:radial-gradient(ellipse,rgba(0,245,255,.15) 0%,transparent 70%)}
.border-top{position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#00f5ff,#bf00ff,#00f5ff,transparent);box-shadow:0 0 20px #00f5ff88}
.border-bottom{position:absolute;bottom:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#bf00ff,#00f5ff,#bf00ff,transparent);box-shadow:0 0 20px #bf00ff88}
.corner{position:absolute;width:40px;height:40px;border-color:#00f5ff;border-style:solid;opacity:.7}
.corner-tl{top:20px;left:20px;border-width:2px 0 0 2px;box-shadow:-4px -4px 12px #00f5ff44}
.corner-tr{top:20px;right:20px;border-width:2px 2px 0 0;box-shadow:4px -4px 12px #00f5ff44}
.corner-bl{bottom:20px;left:20px;border-width:0 0 2px 2px;box-shadow:-4px 4px 12px #00f5ff44}
.corner-br{bottom:20px;right:20px;border-width:0 2px 2px 0;box-shadow:4px 4px 12px #00f5ff44}
.content{position:relative;z-index:10;padding:80px 80px 70px 80px;height:100%;display:flex;flex-direction:column}
.brand{font-family:'Orbitron',monospace;font-size:20px;color:rgba(0,245,255,.5);letter-spacing:.15em;text-transform:uppercase}
.date-badge{font-family:'Orbitron',monospace;font-size:18px;color:rgba(191,0,255,.7);letter-spacing:.1em;border:1px solid rgba(191,0,255,.4);padding:8px 18px;border-radius:4px}
.top-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:100px}
.headline{font-size:82px;font-weight:900;line-height:1.05;margin-bottom:28px;letter-spacing:-.01em;background:linear-gradient(135deg,#00f5ff 0%,#bf00ff 50%,#00ff88 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;filter:drop-shadow(0 0 30px rgba(0,245,255,.4))}
.subtitle{font-size:34px;font-weight:300;color:rgba(255,255,255,.6);line-height:1.6;margin-bottom:60px;max-width:820px}
.neon-line{width:140px;height:2px;background:linear-gradient(90deg,#00f5ff,#bf00ff);box-shadow:0 0 12px #00f5ff;margin-bottom:48px}
.tags{display:flex;flex-wrap:wrap;gap:16px}
.tag{font-family:'Orbitron',monospace;font-size:20px;padding:10px 22px;border:1px solid;border-radius:2px;letter-spacing:.08em;text-transform:uppercase}
.footer{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end}
.footer-brand{font-family:'Orbitron',monospace;font-size:16px;color:rgba(0,245,255,.25);letter-spacing:.1em}
.page-num{font-family:'Orbitron',monospace;font-size:18px;color:rgba(255,255,255,.2)}
</style></head><body>
<div class="grid"></div>
<div class="scanlines"></div>
<div class="glow-top"></div>
<div class="glow-bottom"></div>
<div class="border-top"></div>
<div class="border-bottom"></div>
<div class="corner corner-tl"></div>
<div class="corner corner-tr"></div>
<div class="corner corner-bl"></div>
<div class="corner corner-br"></div>
<div class="content">
  <div class="top-row">
    <span class="brand">Awesome Harness Eng.</span>
    <span class="date-badge">${date}</span>
  </div>
  <div class="headline">${headline}</div>
  <div class="subtitle">${subtitle}</div>
  <div class="neon-line"></div>
  <div class="tags">${tagHtml}</div>
  <div class="footer">
    <span class="footer-brand">每日精选 · AI AGENT 工程实践</span>
    <span class="page-num">1 / 7</span>
  </div>
</div>
</body></html>`;
}

function contentCardB(card, cardNum) {
  const { index, title, body, quote, source } = card;
  const [c1, c2] = NEON_PAIRS[(index-1) % 5];
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Noto+Sans+SC:wght@300;400;700;900&family=Noto+Serif+SC:wght@400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#020010;font-family:'Noto Sans SC',sans-serif;overflow:hidden;position:relative}
.scanlines{position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,245,255,.01) 2px,rgba(0,245,255,.01) 4px);pointer-events:none;z-index:1}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:54px 54px}
.glow-accent{position:absolute;top:-100px;left:-100px;width:700px;height:700px;background:radial-gradient(circle,${c1}18 0%,transparent 65%)}
.glow-accent2{position:absolute;bottom:-200px;right:-100px;width:600px;height:600px;background:radial-gradient(circle,${c2}14 0%,transparent 65%)}
.border-top{position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,${c1},${c2},transparent);box-shadow:0 0 16px ${c1}88}
.corner{position:absolute;width:36px;height:36px;border-style:solid;opacity:.8}
.corner-tl{top:20px;left:20px;border-width:2px 0 0 2px;border-color:${c1};box-shadow:-3px -3px 10px ${c1}44}
.corner-tr{top:20px;right:20px;border-width:2px 2px 0 0;border-color:${c2};box-shadow:3px -3px 10px ${c2}44}
.corner-bl{bottom:20px;left:20px;border-width:0 0 2px 2px;border-color:${c2};box-shadow:-3px 3px 10px ${c2}44}
.corner-br{bottom:20px;right:20px;border-width:0 2px 2px 0;border-color:${c1};box-shadow:3px 3px 10px ${c1}44}
.content{position:relative;z-index:10;padding:80px 80px 60px 80px;height:100%;display:flex;flex-direction:column}
.index-row{display:flex;align-items:center;gap:20px;margin-bottom:48px}
.index-badge{font-family:'Orbitron',monospace;font-size:28px;font-weight:900;width:64px;height:64px;border:2px solid ${c1};border-radius:4px;display:flex;align-items:center;justify-content:center;color:${c1};box-shadow:0 0 20px ${c1}55,inset 0 0 20px ${c1}11}
.index-label{font-family:'Orbitron',monospace;font-size:20px;color:rgba(255,255,255,.3);letter-spacing:.15em}
.big-num{position:absolute;top:60px;right:70px;font-family:'Orbitron',monospace;font-size:120px;font-weight:900;color:${c1};opacity:.06;line-height:1}
.title{font-size:68px;font-weight:900;line-height:1.1;margin-bottom:20px;background:linear-gradient(135deg,${c1},${c2});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;filter:drop-shadow(0 0 20px ${c1}66)}
.neon-line{width:80px;height:2px;background:linear-gradient(90deg,${c1},${c2});box-shadow:0 0 10px ${c1};margin-bottom:40px}
.body{font-family:'Noto Serif SC',serif;font-size:34px;color:rgba(255,255,255,.72);line-height:1.85;margin-bottom:40px;flex:1}
.quote-box{border:1px solid ${c1}44;padding:24px 32px;background:${c1}0d;margin-bottom:28px;position:relative}
.quote-box::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,${c1},${c2})}
.quote-text{font-size:32px;font-weight:700;color:${c1};line-height:1.5;text-shadow:0 0 20px ${c1}66}
.source-row{display:flex;align-items:center;gap:12px}
.source-dot{width:8px;height:8px;border-radius:50%;background:${c1};box-shadow:0 0 8px ${c1}}
.source-text{font-family:'Orbitron',monospace;font-size:20px;color:rgba(255,255,255,.3)}
.footer{display:flex;justify-content:space-between;align-items:center;padding-top:28px;border-top:1px solid rgba(255,255,255,.06)}
.footer-brand{font-family:'Orbitron',monospace;font-size:18px;color:rgba(255,255,255,.2)}
.page-num{font-family:'Orbitron',monospace;font-size:18px;color:rgba(255,255,255,.2)}
</style></head><body>
<div class="grid"></div>
<div class="scanlines"></div>
<div class="glow-accent"></div>
<div class="glow-accent2"></div>
<div class="border-top"></div>
<div class="corner corner-tl"></div>
<div class="corner corner-tr"></div>
<div class="corner corner-bl"></div>
<div class="corner corner-br"></div>
<div class="content">
  <div class="big-num">0${index}</div>
  <div class="index-row">
    <div class="index-badge">${index}</div>
    <span class="index-label">INSIGHT · ${String(index).padStart(2,'0')}</span>
  </div>
  <div class="title">${title}</div>
  <div class="neon-line"></div>
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

function summaryB(summary, articles, date) {
  const points = (summary.points || []).slice(0,4);
  const pointsHtml = points.map((p,i) => {
    const [c1] = NEON_PAIRS[i%5];
    return `<div class="point">
      <span class="point-num" style="color:${c1};border-color:${c1};box-shadow:0 0 12px ${c1}44">${String(i+1).padStart(2,'0')}</span>
      <span class="point-text">${p}</span>
    </div>`;
  }).join('');
  const tags = (summary.hashtags || []).slice(0,6).map((t,i) => {
    const [c1] = NEON_PAIRS[i%5];
    return `<span class="htag" style="color:${c1};border-color:${c1}44;box-shadow:0 0 8px ${c1}22">${t}</span>`;
  }).join('');

  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Noto+Sans+SC:wght@300;400;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#020010;font-family:'Noto Sans SC',sans-serif;overflow:hidden;position:relative}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(0,245,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(0,245,255,.04) 1px,transparent 1px);background-size:54px 54px}
.scanlines{position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,245,255,.01) 2px,rgba(0,245,255,.01) 4px);pointer-events:none}
.rainbow-bar{position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#00f5ff,#bf00ff,#00ff88,#ffdd00,#ff6b35);box-shadow:0 0 20px rgba(0,245,255,.6)}
.content{position:relative;z-index:10;padding:80px 80px 60px 80px;height:100%;display:flex;flex-direction:column}
.title{font-size:64px;font-weight:900;background:linear-gradient(135deg,#00f5ff,#bf00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:12px;filter:drop-shadow(0 0 20px rgba(0,245,255,.5))}
.subtitle{font-family:'Orbitron',monospace;font-size:20px;color:rgba(0,245,255,.4);margin-bottom:48px;letter-spacing:.1em}
.divider{width:100%;height:1px;background:linear-gradient(90deg,rgba(0,245,255,.3),rgba(191,0,255,.3),transparent);margin-bottom:40px}
.points{display:flex;flex-direction:column;gap:24px;margin-bottom:40px}
.point{display:flex;align-items:center;gap:24px}
.point-num{font-family:'Orbitron',monospace;font-size:26px;font-weight:700;width:60px;height:60px;border:2px solid;border-radius:4px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.point-text{font-size:36px;font-weight:700;color:rgba(255,255,255,.85)}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:40px}
.stat{border:1px solid rgba(0,245,255,.15);border-radius:4px;padding:20px;text-align:center;background:rgba(0,245,255,.03)}
.stat-val{font-family:'Orbitron',monospace;font-size:48px;font-weight:700;color:#00f5ff;display:block;text-shadow:0 0 20px #00f5ff88}
.stat-label{font-size:20px;color:rgba(255,255,255,.3);margin-top:6px}
.cta{border:1px solid rgba(0,245,255,.25);padding:24px 32px;background:rgba(0,245,255,.05);margin-bottom:32px}
.cta-text{font-size:32px;color:#00f5ff;font-weight:600;text-shadow:0 0 16px #00f5ff66}
.htags{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:auto}
.htag{font-family:'Orbitron',monospace;font-size:20px;padding:8px 16px;border:1px solid;border-radius:2px}
.footer{display:flex;justify-content:space-between;padding-top:24px;border-top:1px solid rgba(0,245,255,.1)}
.footer-url{font-family:'Orbitron',monospace;font-size:17px;color:rgba(255,255,255,.2)}
.page-num{font-family:'Orbitron',monospace;font-size:17px;color:rgba(255,255,255,.2)}
</style></head><body>
<div class="grid"></div>
<div class="scanlines"></div>
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
  <div class="cta"><div class="cta-text">${summary.cta || '关注我，追踪 AI Agent 工程化最新实践'}</div></div>
  <div class="htags">${tags}</div>
  <div class="footer">
    <span class="footer-url">github.com/liuestc/awesome-harness-engineering</span>
    <span class="page-num">7 / 7</span>
  </div>
</div>
</body></html>`;
}

module.exports = { coverB, contentCardB, summaryB };
