/**
 * Template D: Bento Grid — 2026 流行的苹果风格信息格
 * 设计语言：Apple-inspired Bento Grid
 * 背景：纯白 #FFFFFF / 浅灰 #F5F5F7
 * 强调色：珊瑚橙 #FF6B35 / 深蓝 #1D3557
 * 字体：SF Pro Display 风格（系统无衬线）
 * 特色：不规则大小信息格，圆角卡片，大数字锚点
 */

export function generateBentoCard(data, cardType, index) {
  const accentColor = '#FF6B35';
  const darkColor = '#1D3557';
  const bgColor = '#F5F5F7';

  if (cardType === 'cover') {
    return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px; height: 1350px;
    background: #F5F5F7;
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
    overflow: hidden;
    position: relative;
  }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto auto auto;
    gap: 16px;
    padding: 60px;
    height: 100%;
  }
  .cell {
    background: white;
    border-radius: 28px;
    padding: 36px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
  }
  .cell-hero {
    grid-column: 1 / 3;
    background: ${darkColor};
    min-height: 380px;
    justify-content: flex-start;
  }
  .cell-accent {
    background: ${accentColor};
    min-height: 240px;
  }
  .cell-light {
    background: #E8F4FD;
    min-height: 240px;
  }
  .cell-bottom {
    grid-column: 1 / 3;
    background: white;
    min-height: 160px;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
  .tag {
    display: inline-block;
    background: ${accentColor};
    color: white;
    font-size: 22px;
    font-weight: 600;
    padding: 8px 20px;
    border-radius: 100px;
    margin-bottom: 28px;
    letter-spacing: 0.5px;
  }
  .hero-title {
    font-size: 68px;
    font-weight: 800;
    color: white;
    line-height: 1.1;
    letter-spacing: -2px;
    margin-bottom: 20px;
  }
  .hero-sub {
    font-size: 26px;
    color: rgba(255,255,255,0.65);
    font-weight: 400;
    line-height: 1.5;
  }
  .accent-number {
    font-size: 120px;
    font-weight: 900;
    color: white;
    line-height: 1;
    letter-spacing: -4px;
    opacity: 0.25;
    position: absolute;
    top: 20px;
    right: 30px;
  }
  .accent-label {
    font-size: 28px;
    font-weight: 700;
    color: white;
    line-height: 1.3;
  }
  .accent-sub {
    font-size: 20px;
    color: rgba(255,255,255,0.8);
    margin-top: 8px;
  }
  .light-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  .light-label {
    font-size: 26px;
    font-weight: 700;
    color: ${darkColor};
    line-height: 1.3;
  }
  .light-sub {
    font-size: 19px;
    color: #666;
    margin-top: 8px;
  }
  .bottom-left h3 {
    font-size: 30px;
    font-weight: 700;
    color: ${darkColor};
  }
  .bottom-left p {
    font-size: 20px;
    color: #888;
    margin-top: 6px;
  }
  .bottom-right {
    text-align: right;
  }
  .bottom-right .date {
    font-size: 22px;
    color: #aaa;
    font-weight: 500;
  }
  .bottom-right .brand {
    font-size: 26px;
    font-weight: 800;
    color: ${darkColor};
    margin-top: 4px;
  }
  .dot-pattern {
    position: absolute;
    top: 0; right: 0;
    width: 200px; height: 200px;
    background-image: radial-gradient(circle, rgba(255,255,255,0.15) 2px, transparent 2px);
    background-size: 20px 20px;
    border-radius: 28px;
  }
</style>
</head>
<body>
<div class="grid">
  <div class="cell cell-hero">
    <div class="dot-pattern"></div>
    <div class="tag">每日精选</div>
    <div class="hero-title">${data.title}</div>
    <div class="hero-sub">${data.subtitle}</div>
  </div>
  <div class="cell cell-accent">
    <div class="accent-number">${data.count || '15'}</div>
    <div class="accent-label">今日新增资源</div>
    <div class="accent-sub">经 AI 智能筛选</div>
  </div>
  <div class="cell cell-light">
    <div class="light-icon">⚙</div>
    <div class="light-label">Harness<br>Engineering</div>
    <div class="light-sub">驾驭 AI Agent</div>
  </div>
  <div class="cell cell-bottom">
    <div class="bottom-left">
      <h3>Awesome Harness Engineering</h3>
      <p>每天 10:00 自动更新 · MiniMax-M2.7 驱动</p>
    </div>
    <div class="bottom-right">
      <div class="date">${data.date}</div>
      <div class="brand">Daily Digest</div>
    </div>
  </div>
</div>
</body>
</html>`;
  }

  if (cardType === 'content') {
    const colors = ['#FF6B35', '#1D3557', '#2EC4B6', '#E71D36', '#8338EC'];
    const color = colors[index % colors.length];
    const lightBg = ['#FFF0EB', '#EBF0FF', '#EBFAF9', '#FFEBEE', '#F3EBFF'];
    const bg = lightBg[index % lightBg.length];

    return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px; height: 1350px;
    background: #F5F5F7;
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    padding: 60px;
    gap: 16px;
  }
  .top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .num-badge {
    width: 72px; height: 72px;
    background: ${color};
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    font-weight: 900;
    color: white;
    letter-spacing: -1px;
    flex-shrink: 0;
  }
  .top-tag {
    font-size: 20px;
    color: #999;
    font-weight: 500;
    text-align: right;
  }
  .main-card {
    background: white;
    border-radius: 28px;
    padding: 52px;
    flex: 1;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
    position: relative;
    overflow: hidden;
  }
  .main-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 8px;
    height: 100%;
    background: ${color};
    border-radius: 28px 0 0 28px;
  }
  .card-title {
    font-size: 52px;
    font-weight: 800;
    color: ${darkColor};
    line-height: 1.2;
    letter-spacing: -1.5px;
    margin-bottom: 32px;
  }
  .divider {
    width: 60px;
    height: 4px;
    background: ${color};
    border-radius: 2px;
    margin-bottom: 32px;
  }
  .card-body {
    font-size: 30px;
    color: #444;
    line-height: 1.75;
    flex: 1;
  }
  .quote-box {
    background: ${bg};
    border-radius: 16px;
    padding: 28px 32px;
    margin-top: 32px;
    border-left: 4px solid ${color};
  }
  .quote-text {
    font-size: 26px;
    color: ${color};
    font-weight: 600;
    line-height: 1.6;
    font-style: italic;
  }
  .source-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid #f0f0f0;
  }
  .source-dot {
    width: 10px; height: 10px;
    background: ${color};
    border-radius: 50%;
    flex-shrink: 0;
  }
  .source-text {
    font-size: 20px;
    color: #aaa;
    font-weight: 500;
  }
  .bottom-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: white;
    border-radius: 20px;
    padding: 20px 32px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  }
  .brand-text {
    font-size: 20px;
    font-weight: 700;
    color: ${darkColor};
  }
  .page-text {
    font-size: 20px;
    color: #bbb;
  }
</style>
</head>
<body>
<div class="top-bar">
  <div class="num-badge">0${index + 1}</div>
  <div class="top-tag">Harness Engineering · ${data.date}</div>
</div>
<div class="main-card">
  <div class="card-title">${data.title}</div>
  <div class="divider"></div>
  <div class="card-body">${data.body}</div>
  ${data.quote ? `<div class="quote-box"><div class="quote-text">${data.quote}</div></div>` : ''}
  <div class="source-row">
    <div class="source-dot"></div>
    <div class="source-text">${data.source || 'Awesome Harness Engineering'}</div>
  </div>
</div>
<div class="bottom-row">
  <div class="brand-text">Awesome Harness Engineering</div>
  <div class="page-text">${index + 1} / 5</div>
</div>
</body>
</html>`;
  }

  if (cardType === 'summary') {
    return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px; height: 1350px;
    background: ${darkColor};
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
    overflow: hidden;
    padding: 60px;
    display: flex;
    flex-direction: column;
  }
  .header {
    margin-bottom: 48px;
  }
  .header-tag {
    display: inline-block;
    background: ${accentColor};
    color: white;
    font-size: 22px;
    font-weight: 600;
    padding: 8px 20px;
    border-radius: 100px;
    margin-bottom: 24px;
  }
  .header-title {
    font-size: 56px;
    font-weight: 800;
    color: white;
    line-height: 1.2;
    letter-spacing: -1.5px;
  }
  .resources-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    flex: 1;
  }
  .res-card {
    background: rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px;
    border: 1px solid rgba(255,255,255,0.1);
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .res-type {
    font-size: 18px;
    color: ${accentColor};
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .res-title {
    font-size: 24px;
    font-weight: 700;
    color: white;
    line-height: 1.4;
  }
  .res-score {
    font-size: 18px;
    color: rgba(255,255,255,0.5);
  }
  .footer {
    margin-top: 32px;
    padding-top: 28px;
    border-top: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .footer-brand {
    font-size: 26px;
    font-weight: 800;
    color: white;
  }
  .footer-url {
    font-size: 20px;
    color: rgba(255,255,255,0.4);
  }
</style>
</head>
<body>
<div class="header">
  <div class="header-tag">今日汇总</div>
  <div class="header-title">今日精选资源<br>一览</div>
</div>
<div class="resources-grid">
  ${(data.resources || []).slice(0, 6).map(r => `
  <div class="res-card">
    <div class="res-type">${r.type || 'Article'}</div>
    <div class="res-title">${r.title}</div>
    <div class="res-score">评分 ${r.score || '8.0'} / 10</div>
  </div>`).join('')}
</div>
<div class="footer">
  <div class="footer-brand">Awesome Harness Engineering</div>
  <div class="footer-url">github.com/liuestc/awesome-harness-engineering</div>
</div>
</body>
</html>`;
  }

  return '<html><body>Unknown card type</body></html>';
}
