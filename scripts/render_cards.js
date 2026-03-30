#!/usr/bin/env node
/**
 * render_cards.js
 * 用 Puppeteer 将三套 HTML 模板渲染为 1080×1350 PNG 图片
 *
 * 用法：
 *   node scripts/render_cards.js [date] [template]
 *   date: YYYY-MM-DD（默认今天）
 *   template: a | b | c | all（默认 all）
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const { getFontFaceCSS } = require('./fonts');
const { coverA, contentCardA, summaryA } = require('./templates/template_a_minimal');
const { coverB, contentCardB, summaryB } = require('./templates/template_b_cyberpunk');
const { coverC, contentCardC, summaryC } = require('./templates/template_c_editorial');
const { generateBentoCard } = require('./templates/template_d_bento');
const { generateWarmCard } = require('./templates/template_e_warm');

// ── CLI args ──────────────────────────────────────────────────────────────────
const dateArg = process.argv[2] || new Date().toISOString().slice(0,10);
const templateArg = (process.argv[3] || 'all').toLowerCase();

// ── Load digest data ──────────────────────────────────────────────────────────
const digestDir = path.join(__dirname, '..', 'data', 'daily_digest', dateArg);
const digestFile = path.join(digestDir, 'digest.json');

if (!fs.existsSync(digestFile)) {
  console.error(`[ERROR] digest.json not found: ${digestFile}`);
  console.error('Run crawler.py first to generate digest data.');
  process.exit(1);
}

const digest = JSON.parse(fs.readFileSync(digestFile, 'utf8'));
// Normalize: digest.json wraps data under 'content'
const content = digest.content || digest;
const headline = content.cover?.headline || content.headline || '今日 Harness Engineering 精选';
const subtitle = content.cover?.subtitle || content.subtitle || 'AI Agent 工程化最新实践';
const tags = content.cover?.tags || content.tags || [];
const insights = content.cards || content.insights || [];
const summary = content.summary || {};
const articles = digest.source_articles || digest.articles || [];

// ── Build card list for each template ────────────────────────────────────────
function buildCards(tplName) {
  const cards = [];

  if (tplName === 'a') {
    cards.push({ name: 'card_00_cover', html: coverA({ headline, subtitle, tags, date: dateArg }) });
    (insights || []).slice(0,5).forEach((ins, i) => {
      cards.push({ name: `card_0${i+1}_${i+1}`, html: contentCardA({ ...ins, index: i+1 }, i+2) });
    });
    cards.push({ name: 'card_07_summary', html: summaryA(summary || {}, articles || [], dateArg) });
  } else if (tplName === 'b') {
    cards.push({ name: 'card_00_cover', html: coverB({ headline, subtitle, tags, date: dateArg }) });
    (insights || []).slice(0,5).forEach((ins, i) => {
      cards.push({ name: `card_0${i+1}_${i+1}`, html: contentCardB({ ...ins, index: i+1 }, i+2) });
    });
    cards.push({ name: 'card_07_summary', html: summaryB(summary || {}, articles || [], dateArg) });
  } else if (tplName === 'c') {
    cards.push({ name: 'card_00_cover', html: coverC({ headline, subtitle, tags, date: dateArg }) });
    (insights || []).slice(0,5).forEach((ins, i) => {
      cards.push({ name: `card_0${i+1}_${i+1}`, html: contentCardC({ ...ins, index: i+1 }, i+2) });
    });
    cards.push({ name: 'card_07_summary', html: summaryC(summary || {}, articles || [], dateArg) });
  } else if (tplName === 'd') {
    // Template D: Bento Grid
    const bentoData = { title: headline, subtitle, date: dateArg, count: articles.length || 15 };
    cards.push({ name: 'card_00_cover', html: generateBentoCard(bentoData, 'cover', 0) });
    (insights || []).slice(0,5).forEach((ins, i) => {
      const cardData = {
        title: ins.title || ins.headline || '核心洞见',
        body: ins.body || ins.content || ins.description || '',
        quote: ins.quote || ins.key_quote || '',
        source: ins.source || '',
        type: ins.type || 'Article',
        date: dateArg,
      };
      cards.push({ name: `card_0${i+1}_${i+1}`, html: generateBentoCard(cardData, 'content', i) });
    });
    const summaryData = {
      resources: articles.slice(0,6).map(a => ({
        title: a.title || a.name || '',
        type: a.type || 'Article',
        source: a.source || a.url || '',
        score: a.quality_score || a.score || '8.0',
      }))
    };
    cards.push({ name: 'card_07_summary', html: generateBentoCard(summaryData, 'summary', 0) });
  } else if (tplName === 'e') {
    // Template E: Warm Minimalism
    const warmData = { title: headline, subtitle, date: dateArg, count: articles.length || 15 };
    cards.push({ name: 'card_00_cover', html: generateWarmCard(warmData, 'cover', 0) });
    (insights || []).slice(0,5).forEach((ins, i) => {
      const cardData = {
        title: ins.title || ins.headline || '核心洞见',
        body: ins.body || ins.content || ins.description || '',
        quote: ins.quote || ins.key_quote || '',
        source: ins.source || '',
        type: ins.type || 'Article',
        date: dateArg,
      };
      cards.push({ name: `card_0${i+1}_${i+1}`, html: generateWarmCard(cardData, 'content', i) });
    });
    const summaryData = {
      resources: articles.slice(0,5).map(a => ({
        title: a.title || a.name || '',
        type: a.type || 'Article',
        source: a.source || a.url || '',
        score: a.quality_score || a.score || '8.0',
      }))
    };
    cards.push({ name: 'card_07_summary', html: generateWarmCard(summaryData, 'summary', 0) });
  }

  return cards;
}

// ── Screenshot with Puppeteer ─────────────────────────────────────────────────
async function renderCards(tplName, cards, outDir) {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security', '--allow-file-access-from-files'],
    headless: true,
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1350, deviceScaleFactor: 2 });

  // Inject local font CSS once
  const fontCSS = getFontFaceCSS();

  for (const card of cards) {
    const outPath = path.join(outDir, `${card.name}.png`);
    // Inject local fonts into HTML (replace Google Fonts link)
    const htmlWithFonts = card.html
      .replace(/<link[^>]*fonts\.googleapis[^>]*>/g, '')
      .replace('</head>', `${fontCSS}</head>`);
    await page.setContent(htmlWithFonts, { waitUntil: 'domcontentloaded', timeout: 15000 });
    // Small wait for layout
    await new Promise(r => setTimeout(r, 300));
    await page.screenshot({ path: outPath, type: 'png', clip: { x:0, y:0, width:1080, height:1350 } });
    console.log(`[${tplName.toUpperCase()}] OK → ${path.basename(outPath)}`);
  }

  await browser.close();
}

// ── Main ──────────────────────────────────────────────────────────────────────
(async () => {
  const templates = templateArg === 'all' ? ['a','b','c','d','e'] : [templateArg];

  for (const tpl of templates) {
    const outDir = path.join(digestDir, `template_${tpl}`);
    fs.mkdirSync(outDir, { recursive: true });
    const cards = buildCards(tpl);
    console.log(`\n[INFO] Rendering template ${tpl.toUpperCase()} (${cards.length} cards) → ${outDir}`);
    await renderCards(tpl, cards, outDir);
  }

  console.log(`\n✅ Done! All templates rendered for ${dateArg}`);
})().catch(err => {
  console.error('[ERROR]', err);
  process.exit(1);
});
