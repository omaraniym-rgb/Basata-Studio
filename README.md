# basata.studio

- `site/` is the website. Cloudflare Pages publishes it on every push to `main`.
- `worker/` is the form relay (briefs, Journal newsletter, comments). Cloudflare Workers Builds deploys it on every push to `main`.

Email roles: info@ receives briefs · hello@ talks to clients · journal@ runs the newsletter and comments · press@ for press.

Nothing is pushed to `main` without Omar's yes.
