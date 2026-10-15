# Basata 2.0 — Move to Code

*Drafted 16 Oct 2026. Built from the folder, the Start Here doc, the six-month workplan and the one earlier Claude chat ("What is this", 10 Oct).*

## Goal

Drive stays for **big media and brand masters**. Everything that is text, config or logic moves into **one git repo** that Claude Code can read, edit and ship. Drive stops being the source of truth for anything that has a "latest version".

## What the folder is today (2.8 GB, ~5,100 files)

| Area | What it really is | Today's pain |
|---|---|---|
| **Website** | Static site (`basata-launch`, 42 pages), Journal system (Pages Functions + D1 + KV), form worker v5–v8 as loose files, `basata-so` portfolio (Workers assets), 4 source zips, `upload-steps`, 65 MB `_to_delete` | No history, versions are file names (`-v8.js`), deploys via zip/upload. The README itself says "push to main" but there is no repo here. |
| **Content** | Weekly folders → daily folders → PNG/MP4 named by slot (`08.00 Line.png`). Captions and calendar live in **Notion** | Hand-built per post. 5 posts a day plus reels is a lot of manual production. |
| **3D** | Three.js + Playwright render engine (`lib3d2.html`, `scenes_v*.js`, `libspecs2.py`) producing 88 scenes | Already code. Just unversioned. |
| **Brand** | Mark (.ai/.pdf), photos, videos, email signature HTML, "Visual language" folder (empty) | Rules live only in the Start Here doc. |
| **Plans** | Six-month workplan (md), speaker pitch PDF | Fine. |
| **Archive / `_to_delete`** | Client files, old zips, tgz patches | Dead weight. |
| **Tools** | Empty | |

## Target shape

```
basata/                       ← one git repo (private, GitHub)
├─ site/                      ← basata.studio (Pages)         [from Website/basata-launch + journal-system/functions]
├─ worker/                    ← basata-form (Workers)          [from basata-form-worker-v8 + journal-system/worker]
├─ portfolio/                 ← basata.so (Workers assets)     [from Website/basata-so]
├─ journal-system/lib/        ← shared render/editor code
├─ 3d/                        ← render engine + scene recipes  [from 3D/Working files]
├─ content/
│   ├─ rules.md               ← brand/words/look/rhythm from Start Here (Claude reads this every session)
│   ├─ weeks/2026-10-w2/…     ← per-day post specs (text + which asset), not the PNGs
│   └─ build/                 ← script that renders posts from specs
├─ brand/tokens.json          ← colours, type, spacing (fills the empty "02 Visual language")
├─ plans/                     ← workplans (md)
├─ CLAUDE.md                  ← the Start Here doc, in repo form
└─ README.md
```

Stays on Drive (referenced by path or synced by script, **not** in git): photos, videos, 3D renders, masters (.ai), client archive. Add a `.gitignore` for them.

## Phases

### Phase 0 — Safety (30 min)
1. Zip a snapshot of the whole folder to somewhere outside Drive.
2. Decide the repo home: create the repo **outside** Drive (e.g. `~/Code/basata`). Git inside Google Drive Sync corrupts `.git`. Drive keeps the media; the repo is the code.

### Phase 1 — Skeleton + CLAUDE.md (1 hr)
- `git init`, `.gitignore`, repo layout above.
- Convert the Start Here doc into `CLAUDE.md` (brand rules, words, look, rhythm, folder map). This is what makes every future Claude session already know how Basata works.

### Phase 2 — Website into git (the main win, 2–3 hrs)
1. Pick the live truth: compare `basata-launch/` to what's on basata.studio; `basata-launch.zip`, `basata-studio-source.zip` and `upload-steps` are older snapshots, retire them.
2. Move into `site/`, `worker/` (**only v8**, v5–v7 become git history), `portfolio/`.
3. Merge `journal-system/functions` into `site/functions` as its README intends.
4. Install `wrangler` (not installed), run `wrangler dev` locally to verify forms, Journal and D1.
5. Connect repo → GitHub → Cloudflare Pages / Workers Builds so push-to-`main` deploys. Keep your rule: **nothing pushes to `main` without your yes**, so work happens on branches with preview URLs.
6. Secrets (`RESEND_API_KEY`) stay in Cloudflare, never in the repo.

### Phase 3 — 3D engine (1 hr)
Move `3D/Working files` into `3d/`, add `npm i three@0.169.0` and a one-line `make render SCENE=…`. Output goes to Drive, not git.

### Phase 4 — Content as code (the long game, a few sessions)
- Replace "make PNGs by hand" with **post specs** (`line`, `lesson`, `seen`, `tool`, `closer`) plus a build script that composes photo or 3D scene + text (bottom-left) + mark (top-right) in the 4:5 format.
- Captions: decide Notion (current) vs. markdown in repo. Recommendation: **keep Notion for the calendar, put the text in the repo**, sync later.
- Weekly workflow becomes: write the week's spec → run build → review → publish.

### Phase 5 — Cleanup
- Delete `_to_delete` folders and the superseded zips (after Phase 2 is verified, with your explicit OK).
- Move `Archive` out of the active folder.
- Fill `Tools/` with the scripts that now exist.

## Order I'd do it in
**0 → 1 → 2 → 3 → 5 → 4.** The site is the highest value and lowest risk, and content automation is only worth building once the rules are in `CLAUDE.md`.

## Open questions (answer when we reach them)
1. Which is live on basata.studio right now: `basata-launch/` or something else? The README speaks of `site/`, which doesn't exist here.
2. GitHub account/org for the repo?
3. Keep Notion for captions and calendar, or move fully to the repo?
4. Is `basata-so` (portfolio) a separate live domain, or being merged into basata.studio?
5. Anything in `Archive` you need to keep (client work vs. Basata 2.0)?
