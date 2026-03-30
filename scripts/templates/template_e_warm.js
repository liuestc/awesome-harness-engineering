/**
 * Template E: Warm Minimalism — 2026 流行的暖白极简风
 * 设计语言：Editorial Warm Minimal，类似 Notion / Linear 亮色版
 * 背景：暖白 #FAFAF8 / 米黄 #F7F3EE
 * 强调色：深墨绿 #1A3A2A / 暖橙 #E8622A
 * 字体：衬线大标题 + 无衬线正文（高级杂志感）
 * 特色：大面积留白，细线分隔，手写感装饰元素
 */

export function generateWarmCard(data, cardType, index) {
  const ink = '#1A2B1F';
  const accent = '#E8622A';
  const warmBg = '#FAFAF8';
  const paperBg = '#F7F3EE';

  if (cardType === 'cover') {
    return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('file:///usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px; height: 1350px;
    background: ${warmBg};
    font-family: "Noto Serif CJK SC", "Source Han Serif SC", "Noto Sans CJK SC", serif;
    overflow: hidden;
    position: relative;
  }
  .top-stripe {
    width: 100%;
    height: 8px;
    background: ${ink};
  }
  .content {
    padding: 72px 80px;
    height: calc(100% - 8px);
    display: flex;
    flex-direction: column;
  }
  .meta-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 80px;
  }
  .issue-label {
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 20px;
    font-weight: 600;
    color: ${accent};
    text-transform: uppercase;
    letter-spacing: 3px;
  }
  .date-label {
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 20px;
    color: #999;
    letter-spacing: 1px;
  }
  .divider-line {
    width: 100%;
    height: 1px;
    background: ${ink};
    margin-bottom: 60px;
  }
  .main-title {
    font-size: 88px;
    font-weight: 900;
    color: ${ink};
    line-height: 1.05;
    letter-spacing: -3px;
    margin-bottom: 48px;
    flex: 1;
  }
  .main-title em {
    color: ${accent};
    font-style: normal;
  }
  .subtitle-block {
    border-left: 4px solid ${accent};
    padding-left: 28px;
    margin-bottom: 60px;
  }
  .subtitle-text {
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 28px;
    color: #555;
    line-height: 1.7;
    font-weight: 400;
  }
  .footer-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 32px;
    border-top: 1px solid #ddd;
  }
  .brand {
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: ${ink};
    letter-spacing: 0.5px;
  }
  .count-badge {
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 20px;
    color: white;
    background: ${accent};
    padding: 8px 20px;
    border-radius: 100px;
    font-weight: 600;
  }
  .bg-number {
    position: absolute;
    bottom: 80px;
    right: 60px;
    font-size: 320px;
    font-weight: 900;
    color: rgba(0,0,0,0.04);
    line-height: 1;
    letter-spacing: -10px;
    pointer-events: none;
    font-family: -apple-system, sans-serif;
  }
</style>
</head>
<body>
<div class="top-stripe"></div>
<div class="content">
  <div class="meta-row">
    <div class="issue-label">Daily Digest</div>
    <div class="date-label">${data.date}</div>
  </div>
  <div class="divider-line"></div>
  <div class="main-title">${data.title.replace(/([^\s]{4,})/g, (m, p) => p.length > 6 ? `<em>${p.slice(0,3)}</em>${p.slice(3)}` : m)}</div>
  <div class="subtitle-block">
    <div class="subtitle-text">${data.subtitle}</div>
  </div>
  <div class="footer-row">
    <div class="brand">Awesome Harness Engineering</div>
    <div class="count-badge">今日 ${data.count || 15} 篇精选</div>
  </div>
</div>
<div class="bg-number">${new Date(data.date).getDate() || '29'}</div>
</body>
</html>`;
  }

  if (cardType === 'content') {
    const accentColors = [accent, '#2D6A4F', '#1565C0', '#6A1565', '#C0650A'];
    const col = accentColors[index % accentColors.length];

    return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px; height: 1350px;
    background: ${warmBg};
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", sans-serif;
    overflow: hidden;
    position: relative;
  }
  .top-stripe {
    width: 100%;
    height: 8px;
    background: ${ink};
  }
  .content {
    padding: 60px 80px;
    height: calc(100% - 8px);
    display: flex;
    flex-direction: column;
  }
  .nav-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 48px;
  }
  .nav-brand {
    font-size: 19px;
    color: #aaa;
    font-weight: 500;
    letter-spacing: 0.5px;
  }
  .nav-num {
    font-size: 19px;
    color: #aaa;
  }
  .big-num {
    font-size: 160px;
    font-weight: 900;
    color: ${col};
    line-height: 0.85;
    letter-spacing: -6px;
    margin-bottom: 32px;
    opacity: 0.15;
    position: absolute;
    top: 60px;
    right: 60px;
    font-family: -apple-system, sans-serif;
  }
  .card-title {
    font-size: 58px;
    font-weight: 800;
    color: ${ink};
    line-height: 1.15;
    letter-spacing: -2px;
    margin-bottom: 36px;
    position: relative;
    z-index: 1;
  }
  .accent-line {
    width: 80px;
    height: 5px;
    background: ${col};
    border-radius: 3px;
    margin-bottom: 40px;
  }
  .card-body {
    font-size: 30px;
    color: #444;
    line-height: 1.8;
    flex: 1;
    position: relative;
    z-index: 1;
  }
  .paper-box {
    background: ${paperBg};
    border-radius: 16px;
    padding: 32px 36px;
    margin-top: 36px;
    position: relative;
  }
  .paper-box::before {
    content: '"';
    position: absolute;
    top: -20px;
    left: 28px;
    font-size: 80px;
    color: ${col};
    font-family: Georgia, serif;
    line-height: 1;
    opacity: 0.6;
  }
  .paper-quote {
    font-size: 27px;
    color: #555;
    line-height: 1.7;
    font-style: italic;
    padding-top: 16px;
  }
  .source-row {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 36px;
    padding-top: 28px;
    border-top: 1px solid #e8e4df;
  }
  .source-tag {
    background: ${col};
    color: white;
    font-size: 18px;
    font-weight: 600;
    padding: 5px 14px;
    border-radius: 6px;
    letter-spacing: 0.5px;
  }
  .source-name {
    font-size: 20px;
    color: #999;
  }
  .bottom-stripe {
    width: 100%;
    height: 4px;
    background: linear-gradient(to right, ${col}, transparent);
    margin-top: 40px;
    border-radius: 2px;
  }
</style>
</head>
<body>
<div class="top-stripe"></div>
<div class="content">
  <div class="nav-row">
    <div class="nav-brand">Awesome Harness Engineering</div>
    <div class="nav-num">0${index + 1} / 05</div>
  </div>
  <div class="big-num">0${index + 1}</div>
  <div class="card-title">${data.title}</div>
  <div class="accent-line"></div>
  <div class="card-body">
    ${data.body}
    ${data.quote ? `<div class="paper-box"><div class="paper-quote">${data.quote}</div></div>` : ''}
  </div>
  <div class="source-row">
    <div class="source-tag">${data.type || 'Article'}</div>
    <div class="source-name">${data.source || 'Awesome Harness Engineering'}</div>
  </div>
  <div class="bottom-stripe"></div>
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
    background: ${paperBg};
    font-family: -apple-system, "PingFang SC", "Noto Sans CJK SC", sans-serif;
    overflow: hidden;
  }
  .top-stripe { width: 100%; height: 8px; background: ${ink}; }
  .content { padding: 60px 80px; height: calc(100% - 8px); display: flex; flex-direction: column; }
  .header { margin-bottom: 48px; }
  .header-label {
    font-size: 20px;
    font-weight: 600;
    color: ${accent};
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 16px;
  }
  .header-title {
    font-size: 60px;
    font-weight: 800;
    color: ${ink};
    line-height: 1.15;
    letter-spacing: -2px;
  }
  .divider { width: 100%; height: 1px; background: #ddd; margin-bottom: 36px; }
  .res-list { flex: 1; display: flex; flex-direction: column; gap: 20px; }
  .res-item {
    display: flex;
    align-items: flex-start;
    gap: 24px;
    padding: 24px 28px;
    background: white;
    border-radius: 16px;
    border-left: 4px solid ${accent};
  }
  .res-num {
    font-size: 28px;
    font-weight: 900;
    color: ${accent};
    min-width: 40px;
    opacity: 0.5;
    font-family: -apple-system, sans-serif;
  }
  .res-info { flex: 1; }
  .res-title { font-size: 26px; font-weight: 700; color: ${ink}; line-height: 1.4; }
  .res-meta { font-size: 19px; color: #999; margin-top: 6px; }
  .res-score {
    font-size: 20px;
    font-weight: 700;
    color: ${accent};
    min-width: 60px;
    text-align: right;
    padding-top: 4px;
  }
  .footer {
    padding-top: 28px;
    border-top: 1px solid #ddd;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .footer-brand { font-size: 22px; font-weight: 700; color: ${ink}; }
  .footer-url { font-size: 19px; color: #bbb; }
</style>
</head>
<body>
<div class="top-stripe"></div>
<div class="content">
  <div class="header">
    <div class="header-label">Today's Resources</div>
    <div class="header-title">今日精选<br>资源汇总</div>
  </div>
  <div class="divider"></div>
  <div class="res-list">
    ${(data.resources || []).slice(0, 5).map((r, i) => `
    <div class="res-item">
      <div class="res-num">0${i + 1}</div>
      <div class="res-info">
        <div class="res-title">${r.title}</div>
        <div class="res-meta">${r.type || 'Article'} · ${r.source || ''}</div>
      </div>
      <div class="res-score">${r.score || '8.0'}</div>
    </div>`).join('')}
  </div>
  <div class="footer">
    <div class="footer-brand">Awesome Harness Engineering</div>
    <div class="footer-url">github.com/liuestc/awesome-harness-engineering</div>
  </div>
</div>
</body>
</html>`;
  }

  return '<html><body>Unknown card type</body></html>';
}
