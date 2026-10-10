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
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.png" sizes="512x512"><link rel="apple-touch-icon" sizes="180x180" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAAAKjElEQVR42u2de0xTaRqHXxCGQqGIzsACXrCgq1jBNXXxhoYqjEVEkeAWSnDjLeANBUFR8ZY4IxgzbBYbi6MsVXFZSPEWubiyS7IOUURNULkYtzIIqCsXEQvoCPsHzrox3qDtOaft7/mLQM/3vufrw3c55zvfsejv7ycAPoQlqgBADgA5AOQAkANADgA5AOQAkANADgA5AIAcAHIAyAEgB4AcAHIAyAEgB4AcAHIAADkA5ACQA0AOADkA5ACQA0AOADkA5AAAcgDIASAHgBwAcgDIASAHgBwAcgCTxwpVwC5VVVXl5eUikSgoKAhygHccPHgwPT194OfAwMBDhw6NGTOGO+lZYHtrtigoKFi7du17v0xJSUlKSoIcZs3169cXLlz4wT/NnTtXpVIJBALIYY40NTXNmzevra3tYx8YN25cfn6+UCjEbMW8ePLkSWho6CfMICKNRrNgwYK7d++i5TAjnj17JpVKHzx48CUfdnR0LCoqmjhxIuQwfdrb24ODg+vq6r78EBcXl4qKiuHDh6NbMWU6OzsXL148KDMG+qD169djzGHKvHjxIjQ09N69e0M4tqioKC8vD92KaaLVasPDw69duzbkEpydnauqqvh8PloOUyMyMlIXM4jo6dOnSqUSLYepIZPJSktLdS/HwcGhurqa4StjaDkMxZs3b6Kjo/VixsCo5fTp0+hWTIS4uLhLly7psUCVSgU5jJ6+vr61a9cWFBTot9i6urrBzoQhB+dYtWqV3s0Y4PLly5DDWOnp6ZHJZOfOnTNQ+TrOegYLFvvojfb29vDw8Nu3bxsuxBfelEHLwS00Gs38+fMNagYRtba2ouUwMmpra0NCQj59F15f02PIYWRmSKXS58+fMxDLwcEB3YrRUF1dzZgZRMTw8mPIodPEMjg4mDEziMjX1xdyGAEZGRkymezly5dMBp01axaT4XDjbSjExcUxv8bCxsZGo9HweDwMSDlKW1tbZGRkZWUl86GDgoKYNANyDI76+vply5Y1NzezEn316tUMR8SY40spKyuTSCRsmeHt7e3v7w85uIhKpYqIiNBqtWwlEB8fz3xQDEg/z65duxQKBYsJuLm53blzh/m4GHN8Cq1Wu3LlSn2t5hoyWVlZrMSFHB+lsbExKiqK9WcSN2/ezPDlDXQrn6GioiIyMrKzs5PdNMRicXFxsaUlO0NDDEg/gEKhWLRoEetmuLi45OTksGUGupX36e7u3rhxo1qtZj0TgUCgVqtdXV1ZzAFyvKOhoSEqKqqmpob1TPh8fn5+/qRJk9hNA93KW4qKivz9/blgxsiRIy9fvjx9+nTWM4EcRES7d++Wy+VdXV2sZyIUCsvKyljckwPdyjsePny4YsWK6upqLiQjFovz8vKcnJw4Ujlm3XKcPHlyzpw5HDEjNDS0tLSUO2aYb8vR0tKyadOmK1eucCSf1NTULVu2cK2WzFGOEydO7Nmzh+FFXB9j2rRpSqXS09OTgxVlXnJoNJrY2FhWlup8oEe3tExISEhOTray4ui3YC5yvHr16vDhwxkZGa9fv+ZCPkKhMDs7e8qUKVyuNLMYkF64cGHmzJmHDh3iiBkJCQk3btzguBmm33JcvXo1NTXV0E8pfjlTp07NzMz09vY2itozWTlu3bq1f//+8vJyjuQjEAhSU1NXrVplRHVognLcv39/3759+t1VRxesra1Xrly5bds2tvaahRxvJyMHDhzgwj3V/7FkyZK9e/eOHTvWGOvTRORobm5OS0vLzc1l+Dn0T+Dh4ZGZmcnWIi7IQUTU2tqanp5+7NgxTmW1c+fOxMREY69bI5ajs7MzIyPj6NGjPT093MlKLpcnJyePHj3aBNpjo5Sjo6NDoVBkZWWxvpLvPS0SExM9PDxMZgxnZHI0NTUdOXIkOzu7t7eXU1ps3brVSEedpiBHeXn58ePHL1261NfXx5GULCwswsPDt2/fzvr7tsxUjq6urtzcXKVSqdFoOJXY0qVLU1JSxo8fT6YLd+VobGxUKpWnTp3i1MCCz+fLZLLY2Fhu3mQ3fTlqa2sPHz5cWFjInR5k4LrFmjVroqOjGd61DXK8pbi4OCcnp6SkhFNZzZw5c8OGDVKpdOhFPKmnW4XU0UTadtK20+sesnMiOyfij6CxYvIJIWse5PgwlZWVZ86cUavVnOpBiCgiImL9+vU+Pj5DPL6tkW7kUeUZ+vnmpz7GE9Dvwmh6JE2cT8M49O/K8rOyKpVKoVDU19dzygmBQCCXy9etW+fu7j7EInq7qCSd/v4D9Q7mcQfPWbQsnbxmm7UcDQ0NarVaqVQ+ffqUU1r4+/vL5fLly5cPvYhfXtE/j1DR99T1nyGWMCWEwr4nd5HZyaHRaJKSksrKyjjlhJubW1RUVExMzKhRo3QqqL+fzu2iou90TWi4O8WXkNtkM5KjtrY2MDCQI8u+icjV1TUsLCwkJGTGjBl6KO6XV/SjjG4V6ic5noDW/JVEUnORIyYm5uLFi6w74e7uHhYWFhoaKhaL9VmuMoJu6vUdPJZWlPgP8ppjFnJ4e3s/fvyYlfPk8XizZ88OCAiQSCQGeRL1wl66uE//xdp/TTtv0ojRpi+Hh4cHw5NVHx8ff39/iUQSEBBgwDBV+ZS13FCFj55KyT/RV7Ymfp1DIpGcPXvWoCHs7e3FYrGfn5+fn59YLLa3tzf4WXU/J5Uht49tvE0labR4r4m3HPfv3583b55+1+bY2dmJRCKRSOTj4+Pr68vwewUM2KH8P7aOtK+GHF1NWQ4iqqmpSUtLO3/+/NAOt7GxEQqFnp6eEyZMGHDCy8uLzcFt5xNKnUA9hu8rJfH0hwwTl2MArVb76NGj5ubmlpaWlpaWjo6OF7/S3d1ta2tra2vL4/Hs7Ox4PB6fz3d2dvb09PTy8mL4bTSfJ28zlf2JiUDWPDrwb4YbD2w1qRsHZ5CGqdd5rj5D02VMnhy2fdKB5y3MmUFEd4sZPj/IoQO3zzEa7l4pMdvMQw7dJpkMN1RtDZDDSOhk/Grv88eQA3JwIiLkMJr/Y7QcRoXjb0w7IuTQAQHjcoz0gByQgxMRIYcOCGcwbYbABXIYCZMWMBrOdwlZWEAOI8FpFI3zYy6caCHD5wc5dGMyU1/YMGv6rQRyGBULthBPwEigBLIVQA6jwtaRpCkGj8JzIOkO5k8OcujM/M3k4GzYENIdzDcbkEMfWPNoxQkDziM8Z1MgOxsTQg59MGURLf3OICXbf01xhTTMGnIYMwu30/RIfX85VhRXSA7fsHVOkEN//PEv9PsovZXGH0HxJSw+C0lYYKx/yv5Mf9tC/brtsu0ygeJLaSTLe1dCDgPw801SrabGW0M51sqGArdS8A76yo7184AchqG/j/71IxXuoJetgzhq8rcUqaBvuLKrKeQwJC/bqCqf7hZTzRXqffHRj7mJaPK3NHUpuyMMyMEeD36izif0su3tboL8X3cTdBOR0yhupgw5AKayAHIAyAEgB4AcAHIAyAEgB4AcAHIAADkA5ACQA0AOADkA5ACQA0AOADkA5AAAcgDIASAHgBwAcgDIASAHgBwAcgDIAQDkAJADQA4AOQDkAJADQA4AOQDkAJADmDH/BSKAiTf7hCrqAAAAAElFTkSuQmCC"><link rel="manifest" href="/manifest.webmanifest"><meta name="apple-mobile-web-app-title" content="Basata Studio">
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
