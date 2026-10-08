// Basata Studio form relay. Emails each brief to info@basata.studio
// and sends the client a branded confirmation from hello@basata.studio via Resend.
// Addresses: info@ = brief inbox · hello@ = talks to clients · journal@ = newsletter and comments.
// v5: optional client file (1 file, up to 10 MB) attached to the brief.
// v6: every brief is logged to D1 (binding BRIEFS → basata-briefs) so it can be put on the calendar.
// v7: POST /subscribe {email} → Journal newsletter list (D1 table subscribers) + a one-line welcome.
// v8: GET /comments?slug=… and POST /comments {slug,name,email,body} → Journal comments (D1 table comments). Members only: the email must be on the subscribers list. A comment stays hidden until the commenter clicks the confirm link sent to that email; then it is public and journal@ is told. GET /member?email= says whether an email has joined.
// Secret needed: RESEND_API_KEY (Settings → Variables and Secrets). KV binding: LOVE → basata-love.
const ALLOWED = ['https://basata.studio', 'https://www.basata.studio', 'https://basata-studio.pages.dev'];
let LOGO_B64 = null;
async function logo(){ if (LOGO_B64) return LOGO_B64; try { const b = new Uint8Array(await (await fetch('https://basata.studio/email/mark.png')).arrayBuffer()); let s=''; for (const x of b) s+=String.fromCharCode(x); LOGO_B64 = btoa(s); } catch (e) { LOGO_B64 = ''; } return LOGO_B64; }
const FROM = 'Basata Studio <info@basata.studio>';
const HELLO = 'Basata Studio <hello@basata.studio>';
const JOURNAL = 'Basata Journal <journal@basata.studio>';
const TPL = "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<meta name=\"color-scheme\" content=\"light\">\n<title>We have your brief \u2014 Basata Studio</title>\n</head>\n<body style=\"margin:0;padding:0;background:#f7f6f3;-webkit-text-size-adjust:100%\">\n<div style=\"display:none;max-height:0;overflow:hidden\">Thank you. Your brief is with us and we will reply within two working days.</div>\n<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"background:#f7f6f3\">\n<tr><td align=\"center\" style=\"padding:40px 16px\">\n  <table role=\"presentation\" width=\"560\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"width:100%;max-width:560px;background:#ffffff;border-radius:4px\">\n    <tr><td align=\"right\" style=\"padding:32px 32px 0\"><img src=\"cid:basata-logo\" width=\"44\" alt=\"Basata Studio\" style=\"display:block;width:44px;height:auto;border:0\"></td></tr>\n    <tr><td style=\"padding:40px 40px 0;font-family:Helvetica,Arial,sans-serif;color:#111111\">\n      <h1 style=\"margin:0 0 24px;font-size:34px;line-height:1.05;font-weight:700;letter-spacing:-1px\">Thank you,<br>{{name}}.</h1>\n      <p style=\"margin:0 0 16px;font-size:16px;line-height:1.6;color:#111111\">Your brief for {{company}} has reached us.</p>\n      <p style=\"margin:0 0 16px;font-size:16px;line-height:1.6;color:#111111\">We read every brief ourselves. Within two working days, we will reply with a few questions or a time to talk.</p>\n      <p style=\"margin:0 0 32px;font-size:16px;line-height:1.6;color:#111111\">There is nothing more you need to do for now.</p>\n    </td></tr>\n    <tr><td style=\"padding:0 40px\"><div style=\"height:1px;background:#e8e6e1;line-height:1px;font-size:1px\">&nbsp;</div></td></tr>\n    <tr><td style=\"padding:24px 40px 44px;font-family:Helvetica,Arial,sans-serif\">\n      <p style=\"margin:0;font-size:15px;line-height:1.5;font-weight:700\"><a href=\"https://basata.studio\" style=\"color:#111111;text-decoration:none\">Basata Studio</a></p>\n    </td></tr>\n  </table>\n  <p style=\"margin:20px 0 0;font-family:Helvetica,Arial,sans-serif;font-size:11px;line-height:1.5;color:#9a9893\">You are receiving this because you sent a project brief at basata.studio.</p>\n</td></tr>\n</table>\n</body>\n</html>\n";
const esc = s => String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function cors(origin){ const o = ALLOWED.includes(origin) ? origin : ALLOWED[0];
  return {'Access-Control-Allow-Origin': o, 'Access-Control-Allow-Methods': 'GET, POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type, Accept', 'Vary': 'Origin'}; }
export default {
  async fetch(req, env) {
    const h = cors(req.headers.get('Origin') || '');
    if (req.method === 'OPTIONS') return new Response(null, {headers: h});
    const path = new URL(req.url).pathname;
    if (path === '/member' && req.method === 'GET') {      // is this email on the Journal list?
      const em = String(new URL(req.url).searchParams.get('email') || '').trim().toLowerCase();
      let ok = false;
      if (env.BRIEFS && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) { try { ok = !!(await env.BRIEFS.prepare('SELECT 1 FROM subscribers WHERE email=? AND unsubscribed=0').bind(em).first()); } catch {} }
      return Response.json({member: ok}, {headers: {...h, 'Cache-Control':'no-store'}});
    }
    if (path === '/comments/confirm' && req.method === 'GET') { // commenter clicked the link in their email
      const t = String(new URL(req.url).searchParams.get('t') || '');
      let slug = '';
      if (env.BRIEFS && /^[a-f0-9]{32}$/.test(t)) {
        const row = await env.BRIEFS.prepare('SELECT id,slug,name,email,body,approved FROM comments WHERE token=?').bind(t).first();
        if (row) {
          slug = row.slug;
          if (!row.approved) {
            await env.BRIEFS.prepare('UPDATE comments SET approved=1 WHERE id=?').bind(row.id).run();
            if (env.RESEND_API_KEY) { try { await fetch('https://api.resend.com/emails', {method:'POST', headers:{'Authorization':'Bearer '+env.RESEND_API_KEY,'Content-Type':'application/json'}, body: JSON.stringify({from: JOURNAL, to:['journal@basata.studio'], subject:'Journal comment · '+row.slug, text: row.name+' <'+row.email+'> wrote on /journal/'+row.slug+'/:\n\n'+row.body+'\n\nTo remove it: UPDATE comments SET approved=0 WHERE id='+row.id+';'})}); } catch {} }
          }
        }
      }
      return Response.redirect(slug ? 'https://basata.studio/journal/'+slug+'/?c=1#comments' : 'https://basata.studio/journal/', 302);
    }
    if (path === '/comments') {                             // Journal comments
      const u = new URL(req.url);
      if (req.method === 'GET') {
        const slug = String(u.searchParams.get('slug') || '');
        if (!/^[a-z0-9-]{1,80}$/.test(slug) || !env.BRIEFS) return Response.json({comments:[]}, {headers:h});
        const r = await env.BRIEFS.prepare('SELECT id,name,body,created_at FROM comments WHERE slug=? AND approved=1 ORDER BY id ASC LIMIT 200').bind(slug).all();
        return Response.json({comments: r.results || []}, {headers: {...h, 'Cache-Control':'no-store'}});
      }
      if (req.method !== 'POST') return new Response(null, {status:405, headers:h});
      let b = {}; try { b = await req.json(); } catch {}
      if (b._gotcha) return Response.json({ok:true}, {headers:h});
      const slug = String(b.slug || ''); const name = String(b.name || '').trim().replace(/\s+/g,' ').slice(0,60);
      const em = String(b.email || '').trim().toLowerCase();
      const body = String(b.body || '').trim().replace(/\r/g,'').slice(0,1200);
      if (!/^[a-z0-9-]{1,80}$/.test(slug) || body.length < 2 || name.length < 1) return Response.json({ok:false,error:'body'}, {status:400, headers:h});
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em) || em.length > 120) return Response.json({ok:false,error:'email'}, {status:400, headers:h});
      if (env.BRIEFS) { try { const m = await env.BRIEFS.prepare('SELECT 1 AS ok FROM subscribers WHERE email=? AND unsubscribed=0').bind(em).first(); if (!m) return Response.json({ok:false,error:'member'}, {status:403, headers:h}); } catch { return Response.json({ok:false,error:'member'}, {status:403, headers:h}); } }
      if (/https?:\/\/|www\./i.test(body) && (body.match(/https?:\/\//gi)||[]).length > 1) return Response.json({ok:false,error:'links'}, {status:400, headers:h});
      const ip = req.headers.get('CF-Connecting-IP') || ''; let iph = '';
      try { const dg = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(ip + slug)); iph = [...new Uint8Array(dg)].slice(0,8).map(x=>x.toString(16).padStart(2,'0')).join(''); } catch {}
      const now = new Date().toISOString();
      const tok = [...crypto.getRandomValues(new Uint8Array(16))].map(x=>x.toString(16).padStart(2,'0')).join('');
      if (env.BRIEFS) {
        try { const rc = await env.BRIEFS.prepare("SELECT COUNT(*) AS n FROM comments WHERE ip_hash=? AND created_at > ?").bind(iph, new Date(Date.now()-600000).toISOString()).first(); if (rc && rc.n >= 3) return Response.json({ok:false,error:'slow'}, {status:429, headers:h}); } catch {}
        await env.BRIEFS.prepare('INSERT INTO comments (slug,name,email,body,created_at,approved,ip_hash,token) VALUES (?,?,?,?,?,0,?,?)').bind(slug, name, em, body, now, iph, tok).run();
      }
      if (env.RESEND_API_KEY) { try { const link = 'https://basata-form.basstastudio.workers.dev/comments/confirm?t='+tok;
        const ct = 'Publish your comment\n\nYou wrote on the Basata Journal:\n\n'+body+'\n\nTo publish it, open this link:\n'+link+'\n\nIf this was not you, ignore this email and nothing will be posted.\n\nBasata Studio';
        const chtml = `<div style="background:#f7f6f3;padding:32px 16px"><table role="presentation" width="100%" style="max-width:560px;margin:0 auto;background:#fff;border-radius:4px" cellpadding="0" cellspacing="0"><tr><td align="right" style="padding:28px 32px 0"><img src="cid:basata-logo" width="40" alt="Basata Studio" style="display:block;width:40px;height:auto;border:0"></td></tr><tr><td style="padding:32px 40px 40px;font-family:Helvetica,Arial,sans-serif;color:#111"><h1 style="margin:0 0 20px;font-size:28px;line-height:1.1;font-weight:700;letter-spacing:-.6px">Publish your comment.</h1><p style="margin:0 0 18px;font-size:15px;line-height:1.6;color:#555;white-space:pre-wrap;border-left:2px solid #ff6600;padding-left:14px">${esc(body)}</p><p style="margin:0 0 28px"><a href="${link}" style="display:inline-block;background:#111;color:#fff;text-decoration:none;font-weight:600;font-size:15px;padding:14px 22px;border-radius:12px">Publish comment <span style="color:#ff6600">&#9679;</span></a></p><p style="margin:0;font-size:13px;line-height:1.5;color:#9a9893">If this was not you, ignore this email and nothing will be posted.</p></td></tr></table></div>`;
        await fetch('https://api.resend.com/emails', {method:'POST', headers:{'Authorization':'Bearer '+env.RESEND_API_KEY,'Content-Type':'application/json'}, body: JSON.stringify({from: JOURNAL, to:[em], reply_to:'journal@basata.studio', subject:'Publish your comment — Basata Journal', html: chtml, text: ct, attachments:[{filename:'basata.png', content: await logo(), content_id:'basata-logo', content_type:'image/png'}]})}); } catch {} }
      return Response.json({ok:true, pending:true}, {headers:h});
    }
    if (req.method !== 'POST') return new Response('Basata form relay', {headers: h});
    if (new URL(req.url).pathname === '/love') {            // a quiet heart: count only, never shown
      let b = {}; try { b = await req.json(); } catch {}
      const p = String(b.p || '');
      if (env.LOVE && /^[a-z0-9-]{1,48}$/.test(p)) {
        const n = parseInt(await env.LOVE.get(p) || '0', 10) + 1;
        await env.LOVE.put(p, String(n));
      }
      return new Response(null, {status: 204, headers: h});
    }
    if (new URL(req.url).pathname === '/subscribe') {       // Journal newsletter
      let b = {}; try { b = await req.json(); } catch {}
      if (b._gotcha) return Response.json({ok:true}, {headers:h});
      const em = String(b.email || '').trim().toLowerCase();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em) || em.length > 120) return Response.json({ok:false,error:'email'}, {status:400, headers:h});
      let fresh = false;
      if (env.BRIEFS) {
        try { const r = await env.BRIEFS.prepare('INSERT OR IGNORE INTO subscribers (email,created_at,source) VALUES (?,?,?)').bind(em, new Date().toISOString(), String(b.source || 'journal').slice(0,60)).run(); fresh = !!(r.meta && r.meta.changes); } catch (e) {}
      }
      if (fresh && env.RESEND_API_KEY) {
        const wt = 'You are on the list.\n\nOne article a week from Basata Studio, on brands and the thinking behind them. Nothing else.\n\nThe first one is here: https://basata.studio/journal/\n\nBasata Studio\nhttps://basata.studio\n\nReply with stop to stop receiving emails like this.';
        const wh = `<div style="background:#f7f6f3;padding:32px 16px"><table role="presentation" width="100%" style="max-width:560px;margin:0 auto;background:#fff;border-radius:4px" cellpadding="0" cellspacing="0"><tr><td align="right" style="padding:28px 32px 0"><img src="cid:basata-logo" width="40" alt="Basata Studio" style="display:block;width:40px;height:auto;border:0"></td></tr><tr><td style="padding:32px 40px 40px;font-family:Helvetica,Arial,sans-serif;color:#111"><h1 style="margin:0 0 20px;font-size:30px;line-height:1.1;font-weight:700;letter-spacing:-.8px">You are on the list.</h1><p style="margin:0 0 14px;font-size:16px;line-height:1.6">One article a week on brands and the thinking behind them. Nothing else.</p><p style="margin:0 0 28px;font-size:16px;line-height:1.6">The first one is here: <a href="https://basata.studio/journal/" style="color:#111">basata.studio/journal</a></p><p style="margin:0;font-size:15px;font-weight:700"><a href="https://basata.studio" style="color:#111;text-decoration:none">Basata Studio</a></p></td></tr></table><p style="margin:16px 0 0;text-align:center;font:11px Helvetica,Arial,sans-serif;color:#9a9893">Reply with stop to stop receiving emails like this.</p></div>`;
        try { await fetch('https://api.resend.com/emails', {method:'POST', headers:{'Authorization':'Bearer '+env.RESEND_API_KEY,'Content-Type':'application/json'}, body: JSON.stringify({from: JOURNAL, to:[em], reply_to:'journal@basata.studio', subject:'You are on the list — Basata Studio', html: wh, text: wt, attachments:[{filename:'basata.png', content: await logo(), content_id:'basata-logo', content_type:'image/png'}]})}); } catch (e) {}
      }
      return Response.json({ok:true}, {headers:h});
    }
    let d; try { d = await req.json(); } catch { return Response.json({ok:false,error:'bad json'}, {status:400, headers:h}); }
    if (d._gotcha) return Response.json({ok:true}, {headers:h});           // honeypot: pretend success
    const email = String(d.email || '').trim();
    const okEmail = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
    const send = body => fetch('https://api.resend.com/emails', {method:'POST', headers:{'Authorization':'Bearer '+env.RESEND_API_KEY,'Content-Type':'application/json'}, body: JSON.stringify(body)});
    // 1. The brief, to the studio
    const LABELS = [['name','Name'],['email','Email'],['company','Brand / company'],['about','About the brand'],['audience','Audience'],['need','What they need'],['why','Why now'],['timeline','Timeline'],['budget','Budget'],['more','Anything else'],['file','File']];
    const val = v => Array.isArray(v) ? v.join(', ') : String(v == null ? '' : v);
    const rows = LABELS.filter(([k]) => val(d[k]).trim()).map(([k,l]) =>
      `<tr><td style="padding:14px 0;border-top:1px solid #e8e6e1;font:700 11px Helvetica,Arial,sans-serif;letter-spacing:1px;text-transform:uppercase;color:#9a9893;vertical-align:top;width:150px">${l}</td><td style="padding:14px 0;border-top:1px solid #e8e6e1;font:15px/1.55 Helvetica,Arial,sans-serif;color:#111;white-space:pre-wrap">${esc(val(d[k]))}</td></tr>`).join('');
    const briefHtml = `<div style="background:#f7f6f3;padding:32px 16px"><table role="presentation" width="100%" style="max-width:640px;margin:0 auto;background:#fff;border-radius:4px" cellpadding="0" cellspacing="0"><tr><td style="padding:36px 40px 8px;font:700 28px/1.1 Helvetica,Arial,sans-serif;color:#111;letter-spacing:-.5px">New brief<span style="color:#ff6600">.</span></td></tr><tr><td style="padding:0 40px 8px;font:15px Helvetica,Arial,sans-serif;color:#555">${esc(val(d.company)) || 'No company given'} · ${esc(val(d.name))}</td></tr><tr><td style="padding:16px 40px 36px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">${rows}</table></td></tr></table><p style="text-align:center;font:11px Helvetica,Arial,sans-serif;color:#9a9893">Reply to this email to answer the client directly.</p></div>`;
    // Optional file from the client: one file, 10 MB max, no executables
    let att = null;
    if (d._file && typeof d._file.data === 'string') {
      const fname = String(d._file.name || 'file').replace(/[^\w.\- ()]+/g, '_').slice(0, 120) || 'file';
      const bytes = Math.floor(d._file.data.length * 3 / 4);
      const bad = /\.(exe|bat|cmd|com|scr|msi|js|vbs|ps1|sh|jar|apk|dll)$/i.test(fname);
      if (bytes <= 10 * 1024 * 1024 && !bad) att = {filename: fname, content: d._file.data};
    }
    const briefText = LABELS.map(([k,l]) => `${l}: ${val(d[k])}`).join('\n\n') + (att ? `\n\nFile: ${att.filename} (attached)` : '');
    let sent = false;
    if (env.RESEND_API_KEY) {
      try {
        const b = await send({from: FROM, to: ['info@basata.studio'], cc: ['omarani@basata.studio'], ...(okEmail ? {reply_to: email} : {}),
          subject: `New brief — ${val(d.company) || val(d.name) || 'basata.studio'}`, html: briefHtml, text: briefText, ...(att ? {attachments: [att]} : {})});
        sent = b.ok;
      } catch (e) {}
    }
    if (!sent) return Response.json({ok:false,error:'delivery'}, {status:502, headers:h});
    // Log the brief (never the file) so nothing slips past the inbox
    if (env.BRIEFS) {
      try {
        await env.BRIEFS.prepare('INSERT INTO briefs (received_at,name,email,company,about,need,why,audience,timeline,budget,more,file) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)')
          .bind(new Date().toISOString(), val(d.name), email, val(d.company), val(d.about), val(d.need), val(d.why), val(d.audience), val(d.timeline), val(d.budget), val(d.more), att ? att.filename : '').run();
      } catch (e) {}
    }
    // 2. Thank-you, to the client
    if (env.RESEND_API_KEY && okEmail) {
      const name = esc((d.name || '').split(' ')[0] || 'there');
      const company = d.company ? esc(d.company) : 'your brand';
      const html = TPL.replace('{{name}}', name).replace('{{company}}', company);
      const text = `Thank you, ${d.name||''}.\n\nYour brief for ${d.company||'your brand'} has reached us.\n\nWe read every brief ourselves. Within two working days, we will reply with a few questions or a time to talk.\n\nThere is nothing more you need to do for now.\n\nBasata Studio`;
      try { await send({from: HELLO, to: [email], reply_to: 'hello@basata.studio', subject: 'We have your brief — Basata Studio', html, text, attachments:[{filename:'basata.png', content: await logo(), content_id:'basata-logo', content_type:'image/png'}]}); } catch (e) {}
    }
    return Response.json({ok:true}, {headers:h});
  }
};
