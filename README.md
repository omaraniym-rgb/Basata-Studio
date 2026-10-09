# basata.studio

- `site/` is the website. Cloudflare Pages publishes it on every push to `main`.
- `worker/` is the form relay (briefs, Journal newsletter, comments). Cloudflare Workers Builds deploys it on every push to `main`.

Email roles: info@ receives briefs · hello@ talks to clients · journal@ runs the newsletter and comments · press@ for press.

Nothing is pushed to `main` without Omar's yes.

## How updates go live
1. Claude edits `site/` or `worker/` and saves a copy to Drive › Basata 2.0 › Website.
2. On Omar's go, Claude pushes to `main`.
3. Cloudflare publishes: `site/` → Pages project **basata-site** (basata.studio), `worker/` → Worker **basata-form**.

## Journal (live)

- Write at **basata.studio/journal/write**. Sign in with omarani@basata.studio or omaraniym@gmail.com; a one-time link comes from journal@.
- Articles live in D1 (`basata-briefs` → `articles`); images in KV (`basata-media`), served at `/media/…`.
- `/journal/`, each article, `/journal/feed.xml` and `/sitemap.xml` are rendered by Pages Functions (`functions/`, `lib/`), in the same design as the rest of the site.
