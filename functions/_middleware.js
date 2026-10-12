// One home address: anything that reaches the site under another name
// (www.basata.studio, http://, an old domain) moves permanently to
// https://basata.studio, same path. Preview addresses on pages.dev are left alone.
const HOME = 'basata.studio';

export async function onRequest(ctx) {
  const url = new URL(ctx.request.url);
  const host = url.hostname;
  if (host !== HOME && !host.endsWith('.pages.dev') && host !== 'localhost' && host !== '127.0.0.1') {
    return Response.redirect(`https://${HOME}${url.pathname}${url.search}`, 301);
  }
  return ctx.next();
}
