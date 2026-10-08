// The Journal editor: /journal/write
// Login: enter your email, get a one-time link (sent by the form worker), click it, stay signed in 30 days.
import { articlePage } from './render.js';
import { editorPage, loginPage } from './editor.js';

const RELAY = 'https://basata-form.basstastudio.workers.dev';
const DAY = 86400000;
const rand = n => [...crypto.getRandomValues(new Uint8Array(n))].map(x => x.toString(16).padStart(2, '0')).join('');
const json = (o, s = 200) => Response.json(o, { status: s, headers: { 'Cache-Control': 'no-store' } });
const html = (h, extra = {}) => new Response(h, { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex', ...extra } });
const slugify = s => String(s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/['’]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70) || 'untitled';

function cookie(req, name) {
  const m = (req.headers.get('Cookie') || '').match(new RegExp('(?:^|;\\s*)' + name + '=([^;]+)'));
  return m ? m[1] : '';
}

async function who(req, env) {
  const t = cookie(req, 'bj_s');
  if (!/^[a-f0-9]{64}$/.test(t)) return null;
  const r = await env.DB.prepare("SELECT email FROM admin_tokens WHERE token=? AND kind='session' AND expires_at>?").bind(t, Date.now()).first();
  return r ? r.email : null;
}

export async function admin({ request, env }) {
  const url = new URL(request.url);
  const p = url.pathname.replace(/\/+$/, '') || '/';
  const M = request.method;

  // same-origin guard for every state-changing request
  if (M !== 'GET' && M !== 'HEAD') {
    const o = request.headers.get('Origin');
    if (o && o !== url.origin) return json({ ok: false, error: 'origin' }, 403);
  }

  if (p === '/journal/write/login' && M === 'POST') {
    let b = {}; try { b = await request.json(); } catch {}
    const email = String(b.email || '').trim().toLowerCase();
    try {
      await fetch(RELAY + '/admin/link', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, base: url.origin }) });
    } catch {}
    return json({ ok: true }); // same answer either way
  }

  if (p === '/journal/write/auth' && M === 'GET') {
    const t = url.searchParams.get('t') || '';
    const row = /^[a-f0-9]{64}$/.test(t) ? await env.DB.prepare("SELECT email FROM admin_tokens WHERE token=? AND kind='link' AND expires_at>?").bind(t, Date.now()).first() : null;
    if (!row) return html(loginPage('That link has expired or was already used. Ask for a new one.'));
    await env.DB.prepare('DELETE FROM admin_tokens WHERE token=?').bind(t).run();
    const s = rand(32);
    await env.DB.prepare("INSERT INTO admin_tokens (token,email,kind,expires_at) VALUES (?,?, 'session', ?)").bind(s, row.email, Date.now() + 30 * DAY).run();
    return new Response(null, { status: 302, headers: { Location: '/journal/write', 'Set-Cookie': `bj_s=${s}; Path=/journal/write; Max-Age=${30 * 86400}; HttpOnly; Secure; SameSite=Lax` } });
  }

  const me = await who(request, env);

  if (p === '/journal/write' && M === 'GET') return html(me ? editorPage(me) : loginPage());
  if (!me) return json({ ok: false, error: 'login' }, 401);

  if (p === '/journal/write/logout' && M === 'POST') {
    await env.DB.prepare('DELETE FROM admin_tokens WHERE token=?').bind(cookie(request, 'bj_s')).run();
    return new Response(null, { status: 204, headers: { 'Set-Cookie': 'bj_s=; Path=/journal/write; Max-Age=0; HttpOnly; Secure; SameSite=Lax' } });
  }

  if (p === '/journal/write/api/articles' && M === 'GET') {
    const r = await env.DB.prepare('SELECT id,slug,title,status,published_at,updated_at FROM articles ORDER BY COALESCE(published_at, updated_at) DESC').all();
    return json({ articles: r.results || [] });
  }
  if (p === '/journal/write/api/article' && M === 'GET') {
    const a = await env.DB.prepare('SELECT * FROM articles WHERE id=?').bind(+url.searchParams.get('id') || 0).first();
    return a ? json({ article: a }) : json({ ok: false }, 404);
  }
  if (p === '/journal/write/api/preview' && M === 'POST') {
    let a = {}; try { a = await request.json(); } catch {}
    return html(articlePage({ ...a, slug: a.slug || 'preview' }, { preview: true }));
  }
  if (p === '/journal/write/api/save' && M === 'POST') {
    let a = {}; try { a = await request.json(); } catch {}
    const now = new Date().toISOString();
    const f = {
      title: String(a.title || '').trim().slice(0, 200),
      dek: String(a.dek || '').trim().slice(0, 400),
      description: String(a.description || '').trim().slice(0, 400),
      body: String(a.body || '').slice(0, 200000),
      cover: String(a.cover || '').slice(0, 500),
      hero: String(a.hero || '').slice(0, 20000),
    };
    let slug = slugify(a.slug || f.title);
    const clash = await env.DB.prepare('SELECT id FROM articles WHERE slug=? AND id<>?').bind(slug, +a.id || 0).first();
    if (clash) slug = slug + '-' + rand(2);
    let id = +a.id || 0;
    if (id) {
      const cur = await env.DB.prepare('SELECT status,slug FROM articles WHERE id=?').bind(id).first();
      if (!cur) return json({ ok: false, error: 'missing' }, 404);
      if (cur.status === 'published') slug = cur.slug; // a live address never changes
      await env.DB.prepare('UPDATE articles SET slug=?,title=?,dek=?,description=?,body=?,cover=?,hero=?,updated_at=? WHERE id=?')
        .bind(slug, f.title, f.dek, f.description, f.body, f.cover, f.hero, now, id).run();
    } else {
      const r = await env.DB.prepare("INSERT INTO articles (slug,title,dek,description,body,cover,hero,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,'draft',?,?)")
        .bind(slug, f.title, f.dek, f.description, f.body, f.cover, f.hero, now, now).run();
      id = r.meta.last_row_id;
    }
    return json({ ok: true, id, slug, updated_at: now });
  }
  if (p === '/journal/write/api/status' && M === 'POST') {
    let b = {}; try { b = await request.json(); } catch {}
    const id = +b.id || 0;
    if (b.status === 'published') {
      await env.DB.prepare("UPDATE articles SET status='published', published_at=COALESCE(published_at, ?) WHERE id=?").bind(new Date().toISOString(), id).run();
    } else {
      await env.DB.prepare("UPDATE articles SET status='draft' WHERE id=?").bind(id).run();
    }
    const a = await env.DB.prepare('SELECT status,slug,published_at FROM articles WHERE id=?').bind(id).first();
    return json({ ok: true, ...a });
  }
  if (p === '/journal/write/api/delete' && M === 'POST') {
    let b = {}; try { b = await request.json(); } catch {}
    await env.DB.prepare("DELETE FROM articles WHERE id=? AND status='draft'").bind(+b.id || 0).run();
    return json({ ok: true });
  }
  if (p === '/journal/write/api/upload' && M === 'POST') {
    const type = (request.headers.get('Content-Type') || '').split(';')[0];
    const ext = { 'image/webp': 'webp', 'image/jpeg': 'jpg', 'image/png': 'png', 'image/gif': 'gif', 'image/svg+xml': 'svg' }[type];
    if (!ext) return json({ ok: false, error: 'type' }, 415);
    const buf = await request.arrayBuffer();
    if (buf.byteLength > 20 * 1024 * 1024) return json({ ok: false, error: 'size' }, 413);
    const d = new Date();
    const key = `j/${d.getUTCFullYear()}${String(d.getUTCMonth() + 1).padStart(2, '0')}/${rand(8)}.${ext}`;
    await env.MEDIA.put(key, buf, { metadata: { type, by: me } });
    return json({ ok: true, url: '/media/' + key });
  }
  return json({ ok: false, error: 'not found' }, 404);
}
