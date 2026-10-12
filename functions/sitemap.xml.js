// Static sitemap + every published Journal article, kept current automatically.
export async function onRequestGet({ request, env }) {
  const res = await env.ASSETS.fetch(request);
  let xml = await res.text();
  try {
    const r = await env.DB.prepare("SELECT slug, COALESCE(updated_at, published_at) AS m, COALESCE(og, cover) AS img FROM articles WHERE status='published'").all();
    xml = xml.replace(/<url><loc>https:\/\/basata\.studio\/journal\/[a-z0-9-]+\/<\/loc>[\s\S]*?<\/url>\s*/g, '');
    const add = (r.results || []).map(a => `<url><loc>https://basata.studio/journal/${a.slug}/</loc><lastmod>${String(a.m).slice(0, 10)}</lastmod>${a.img ? `<image:image><image:loc>${/^https?:/.test(a.img) ? a.img : 'https://basata.studio' + a.img}</image:loc></image:image>` : ''}</url>`).join('\n');
    // the Journal index changes whenever an article does
    const last = (r.results || []).map(a => String(a.m).slice(0, 10)).sort().pop();
    if (last) xml = xml.replace(/(<loc>https:\/\/basata\.studio\/journal\/<\/loc><lastmod>)[^<]*/, '$1' + last);
    xml = xml.replace('</urlset>', add + '\n</urlset>');
  } catch (e) {}
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8', 'Cache-Control': 'public, max-age=3600' } });
}
