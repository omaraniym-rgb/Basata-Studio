// Basata Journal, served live from the database.
//   /journal/                 index of published articles
//   /journal/<slug>/          an article
//   /journal/feed.xml         RSS
//   /journal/write…           the editor (login by emailed link)
// Anything else under /journal/ (images) falls through to static files.
import { articlePage, indexPage, feed } from '../../lib/render.js';
import { admin } from '../../lib/admin.js';
import { SEED } from '../../lib/seed.js';

const HTML = { 'Content-Type': 'text/html; charset=utf-8' };

export async function onRequest(ctx) {
  const { request, env } = ctx;
  const url = new URL(request.url);
  const p = url.pathname;

  await seed(env);
  if (p === '/journal/write' || p.startsWith('/journal/write/')) return admin(ctx);
  if (request.method !== 'GET' && request.method !== 'HEAD') return ctx.next();

  if (p === '/journal' ) return Response.redirect(url.origin + '/journal/', 301);
  if (p === '/journal/') {
    const list = await published(env);
    return new Response(indexPage(list), { headers: { ...HTML, 'Cache-Control': 'public, max-age=60' } });
  }
  if (p === '/journal/feed.xml') {
    return new Response(feed(await published(env)), { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8', 'Cache-Control': 'public, max-age=300' } });
  }
  const m = p.match(/^\/journal\/([a-z0-9-]{1,80})\/?$/);
  if (m) {
    const a = await env.DB.prepare("SELECT * FROM articles WHERE slug=? AND status='published'").bind(m[1]).first();
    if (a) {
      if (!p.endsWith('/')) return Response.redirect(url.origin + p + '/', 301);
      return new Response(articlePage(a), { headers: { ...HTML, 'Cache-Control': 'public, max-age=60' } });
    }
    // no such article (or still a draft): show the Journal, with a real 404
    const asset = await ctx.next();
    if (asset.status === 200 && !(asset.headers.get('Content-Type') || '').includes('text/html')) return asset;
    return new Response(indexPage(await published(env)), { status: 404, headers: HTML });
  }
  return ctx.next();
}

async function published(env) {
  const r = await env.DB.prepare("SELECT slug,title,dek,cover,body,published_at FROM articles WHERE status='published' ORDER BY published_at DESC LIMIT 200").all();
  return r.results || [];
}

let seeded = false;
async function seed(env) {
  if (seeded) return;
  if (await env.MEDIA.get('sys/seeded')) { seeded = true; return; }
  const n = await env.DB.prepare('SELECT COUNT(*) AS n FROM articles').first();
  if (!n || !n.n) {
    const k = ['slug', 'title', 'dek', 'description', 'body', 'cover', 'og', 'hero', 'status', 'published_at', 'created_at', 'updated_at'];
    await env.DB.prepare(`INSERT OR IGNORE INTO articles (${k.join(',')}) VALUES (${k.map(() => '?').join(',')})`).bind(...k.map(x => SEED[x])).run();
  }
  await env.MEDIA.put('sys/seeded', '1');
  seeded = true;
}
