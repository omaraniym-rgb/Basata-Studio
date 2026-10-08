// Images uploaded from the Journal editor, stored in KV (MEDIA).
export async function onRequestGet({ params, env }) {
  const key = [].concat(params.path || []).join('/');
  if (!/^[a-z0-9/._-]{1,120}$/.test(key)) return new Response('Not found', { status: 404 });
  const { value, metadata } = await env.MEDIA.getWithMetadata(key, { type: 'stream' });
  if (!value) return new Response('Not found', { status: 404 });
  return new Response(value, { headers: { 'Content-Type': (metadata && metadata.type) || 'application/octet-stream', 'Cache-Control': 'public, max-age=31536000, immutable' } });
}
