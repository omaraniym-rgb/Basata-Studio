# Basata 2.0: how we work

Owner: Omar Yusuf (Omarani). Studio site: basata.studio. Drive folder "Basata 2.0" holds media and masters; this repo holds code and text.

## Brand
- The ب mark and the name ba·sa·ta never appear together. The website landing page is the only exception.
- Never use client names, client work or client assets in Basata content.
- Never use Omar's personal photos or camera roll.
- Brand assets must work for any topic. Build them to be reused.

## Words
- Content is never sales. We talk about strategy and design, to entrepreneurs and visionary people.
- Write like a person: informative, respectful, punchy, plain. One sentence per page. No hashtags. Never AI-sounding.
- Personality: giving. Professional, no arrogance.

## Look
- Calm, not shouting. Mark top right, bold text bottom left, no subtitle, no labels.
- One subject per image, with space around it. The text corner stays clear.
- Every stock photo is retouched before it goes public: graded to the Basata palette, then flipped, cropped and placed so it becomes a brand asset.
- In videos, 3D objects move with meaning (a ball climbs stairs, stones stack) with soft light, gentle motion and quiet sound.

## Rhythm
- One theme per month, one sub-topic per week. Weeks start on Saturday.
- Five posts a day (08.00 Line, 11.00 Lesson, 14.00 Seen, 17.00 Tool, 20.00 Closer), one article a week, one reel a week. Friday 14.00 is a Recap carousel instead of a Tool.
- Platforms: Instagram, X, LinkedIn, Facebook, TikTok. TikTok gets the video every time. Instagram/Facebook get stills by default, plus six Reels a week (not Friday). Reels stay out of the Instagram grid. No hashtags.
- File naming: `08.00 Line.png`, `08.00 Line · TikTok.mp4`, carousels `17.00 Tool · slide 1.png`.
- Captions, calendar and posting rules live in Notion (Basata · Content · October 2026). Articles live in the Journal on basata.studio.

## Code and deploys
- Repo: https://github.com/omaraniym-rgb/Basata-Studio (main deploys on push).
- `site/` + `functions/` + `lib/` → Pages project `basata-site` (basata.studio); `worker/` → Worker `basata-form`. The basata.so portfolio (Worker `basata-so`) is not in this repo yet.
- Email roles: info@ receives briefs, hello@ talks to clients, journal@ runs newsletter and comments, press@ for press.
- Journal articles live in D1 (`basata-briefs` → `articles`), images in KV (`basata-media`). Code only in git.
- Never push to `main` without Omar's explicit yes. Work on branches.
- Never commit secrets. RESEND_API_KEY is a Cloudflare secret.

## Migration status
See plans/Basata 2.0 — Move to Code Plan.md. Done: snapshot (~/Backups), repo cloned, CLAUDE.md. The website already lives in git (GitHub), so Phase 2 reduces to checking it. Next: bring in portfolio (basata.so), 3d engine, content specs.
