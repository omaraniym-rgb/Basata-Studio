import { CSS as CSS0, CORNER, FOOT, NL, CM, CM_JS } from './tpl.js';
import { md, esc, words, nowidows } from './md.js';

const CSS = CSS0.replace('.fig img:not([src^="bird"]):not([src^="door"]){border-radius:0}', '');
const SITE = 'https://basata.studio';
const EXTRA_CSS = '.fig img{border-radius:8px}.fig.cut img{border-radius:0}.hero img.cover{display:block;width:100%;height:auto;border-radius:8px}article ol{margin:0 0 1.4em;padding-left:1.3em}article ol li{padding-left:4px}article ol li::before{display:none}article code{font:400 .9em var(--mono)}.jempty{color:var(--fg-2);margin-top:40px}.meta a{color:inherit;text-decoration:none}';

const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export const fmtDate = d => { const x = new Date(d || Date.now()); return `${x.getUTCDate()} ${MON[x.getUTCMonth()]} ${x.getUTCFullYear()}`; };
export const readMin = body => Math.max(1, Math.round(words(body) / 220));
const abs = u => !u ? '' : /^https?:/.test(u) ? u : SITE + (u[0] === '/' ? u : '/' + u);

function head({ title, desc, url, img, type = 'website', ld = [], robots }) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
${type === 'article' ? '<meta name="author" content="Omarani">' : ''}
${robots ? `<meta name="robots" content="${robots}">` : `<link rel="canonical" href="${url}">`}
<meta property="og:type" content="${type}">
<meta property="og:site_name" content="Basata Studio">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${esc(img)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@basatastudio">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.png" sizes="512x512"><link rel="apple-touch-icon" sizes="180x180" href="/basata-icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="apple-mobile-web-app-title" content="Basata Studio">
<link rel="alternate" type="application/rss+xml" title="Basata Journal" href="/journal/feed.xml">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#121211" media="(prefers-color-scheme: dark)"><meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="/fonts/fonts.css">
<style>${CSS}${EXTRA_CSS}</style>
${ld.map(o => `<script type="application/ld+json">${JSON.stringify(o)}</script>`).join('\n')}
</head>
<body>
${CORNER}
`;
}

const nl = src => NL.replace('data-src="journal/vision-made-visible"', `data-src="${esc(src)}"`);
const cm = slug => CM.replace('data-slug="vision-made-visible"', `data-slug="${esc(slug)}"`);

export function articlePage(a, { preview = false } = {}) {
  const url = `${SITE}/journal/${a.slug}/`;
  const desc = a.description || a.dek || '';
  const img = abs(a.og || a.cover) || SITE + '/og.png';
  const date = a.published_at || a.updated_at || new Date().toISOString();
  const mins = readMin(a.body);
  const hero = a.hero ? `<div class="col hero">${a.hero}</div>`
    : a.cover ? `<div class="col hero"><img class="cover" src="${esc(a.cover)}" alt=""></div>` : '';
  const ld = [
    { '@context': 'https://schema.org', '@type': 'Article', headline: a.title, description: desc, datePublished: date.slice(0, 10), dateModified: (a.updated_at || date).slice(0, 10), author: { '@type': 'Person', name: 'Omarani', url: 'https://x.com/omarani' }, publisher: { '@type': 'Organization', name: 'Basata Studio', logo: { '@type': 'ImageObject', url: SITE + '/favicon.png' } }, mainEntityOfPage: url, image: img, articleSection: 'Journal', wordCount: words(a.body) },
    { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Basata Studio', item: SITE + '/' }, { '@type': 'ListItem', position: 2, name: 'Journal', item: SITE + '/journal/' }, { '@type': 'ListItem', position: 3, name: a.title, item: url }] },
  ];
  const page = head({ title: `${a.title} — Basata Journal`, desc, url, img, type: 'article', ld: preview ? [] : ld, robots: preview ? 'noindex' : '' }) + `
<main class="wrap">
<div class="top"></div>
<div class="col">
<h1>${esc(a.title || 'Untitled')}</h1>
${a.dek ? `<p class="dek">${esc(a.dek)}</p>` : ''}
<p class="meta"><a href="https://x.com/omarani" target="_blank" rel="author noopener">OMARANI</a> &middot; ${fmtDate(date).toUpperCase()} &middot; ${mins} MIN READ</p>
</div>
${hero}
<article class="col">
${md(a.body)}
${preview ? '' : cm(a.slug)}
</article>
${preview ? '' : nl('journal/' + a.slug)}
${preview ? '' : `<script>${CM_JS}</script>`}
<div class="col">${FOOT}</div>
</main>
</body>
</html>`;
  return nowidows(page);
}

export function indexPage(list) {
  const url = SITE + '/journal/';
  const ld = [{ '@context': 'https://schema.org', '@type': 'Blog', name: 'Basata Journal', url, description: 'Articles on brands and the thinking behind them, by Basata Studio.', publisher: { '@type': 'Organization', name: 'Basata Studio', url: SITE + '/' }, blogPost: list.map(a => ({ '@type': 'BlogPosting', headline: a.title, url: `${SITE}/journal/${a.slug}/`, datePublished: (a.published_at || '').slice(0, 10) })) }];
  const cards = list.map(a => `<li><a class="jcard" href="/journal/${esc(a.slug)}/">${a.cover ? `<img src="${esc(a.cover)}" alt="" loading="lazy">` : ''}<div><b>${esc(a.title)}</b>${a.dek ? `<span>${esc(a.dek)}</span>` : ''}<i>${fmtDate(a.published_at)} · ${readMin(a.body)} min</i></div></a></li>`).join('\n');
  const page = head({ title: 'Journal — Basata Studio', desc: 'Articles on brands and the thinking behind them. From Basata Studio.', url, img: SITE + '/og.png', ld }) + `
<main class="wrap">
<div class="top"></div>
<div class="col">
<h1>Journal</h1>
<p class="dek">Brands, and the thinking behind them. Plain words, one idea at a time.</p>
${list.length ? `<ul class="jlist">\n${cards}\n</ul>` : '<p class="jempty">The first article is on its way.</p>'}
</div>
${nl('journal')}
<div class="col">${FOOT}</div>
</main>
</body>
</html>`;
  return nowidows(page);
}

export function feed(list) {
  const items = list.map(a => `<item><title>${esc(a.title)}</title><link>${SITE}/journal/${a.slug}/</link><guid>${SITE}/journal/${a.slug}/</guid><pubDate>${new Date(a.published_at).toUTCString()}</pubDate><description>${esc(a.dek || a.description || '')}</description></item>`).join('');
  return `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Basata Journal</title><link>${SITE}/journal/</link><description>Brands, and the thinking behind them.</description>${items}</channel></rss>`;
}
