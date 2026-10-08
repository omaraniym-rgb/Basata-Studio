# basata.studio

- `site/` is the website. Cloudflare Pages publishes it on every push to `main`.
- `worker/` is the form relay (briefs, Journal newsletter, comments). Cloudflare Workers Builds deploys it on every push to `main`.

Email roles: info@ receives briefs · hello@ talks to clients · journal@ runs the newsletter and comments · press@ for press.

Nothing is pushed to `main` without Omar's yes.

## How updates go live
1. Claude edits `site/` or `worker/` and saves a copy to Drive › Basata 2.0 › Website.
2. On Omar's go, Claude pushes to `main`.
3. Cloudflare publishes: `site/` → Pages project **basata-site** (basata.studio), `worker/` → Worker **basata-form**.
