# The Vivisection Lab — build notes & morning briefing

*Built overnight 2026-05-31 while you slept. This is the "what I did / what's left / your call" doc. Read top to bottom; it's ordered by what matters.*

---

## TL;DR

I turned your three bodies of work into a **4-page static site** that matches the Gemma "Surgical Record" look, and I **finished the granite analysis** you hadn't done yet (the overnight sweep data was sitting there unanalyzed — it has a real new result). Nothing destructive: I did **not** touch your live `RYS-vivisection-experiments` repo. The draft is a separate folder you can open in a browser right now.

**Open it:** the preview server is already running → http://localhost:8013  (or just double-click `index.html`).

**The one new scientific result:** granite's overnight round produced a champion config — `combo_10_38` — that beats every single layer on emotional-reasoning while leaving factual recall untouched, plus a clean dose-response curve showing one extra copy of a layer is medicine and two is poison. Details in §"What I added to the science" below.

---

## What's in this folder

```
vivisection-site/
├── index.html        ← NEW hub / landing page (the front door)
├── granite.html      ← NEW full granite page (vivisection + sweep + new data)
├── hrm.html          ← NEW HRM page, badged DRAFT (your call to publish)
├── gemma.html        ← your existing live page, copied verbatim + a back-nav bar
├── assets/
│   ├── lab.css        ← the design system, extracted from your Gemma page + additions
│   ├── lab.js         ← tiny: dark/light toggle (persists)
│   ├── granite_layermap.svg   ← data-driven, generated from the sweep JSONL
│   ├── granite_dose.svg       ← data-driven dose-response
│   ├── make_granite_figs.py   ← regenerates those two SVGs from the data
│   └── hrm/*.png      ← 3 figures copied from HRM-mlx/figs (framed, not redrawn)
└── BUILD_NOTES.md    ← this file
```

The pages use **relative links only** (`granite.html`, `assets/…`), so the folder drops into any repo or path unchanged — you don't have to decide the hosting URL before it works.

---

## Platform decision (you asked: SPA / multi-repo / Cloudflare / AWS?)

**Recommendation: multi-page static site on GitHub Pages. Don't do SPA, don't migrate to Cloudflare/AWS.** Reasoning, briefly:

- **These are documents, not an app.** The only interactivity is a theme toggle and accordions — both work as plain static HTML + a few lines of JS. An SPA buys you nothing here and adds the classic Pages deep-link-404 problem + a build step. Skip it.
- **You already have GitHub Pages working.** Lowest friction, no new accounts, no DNS, no pipeline. For *static multi-page*, Cloudflare Pages / Netlify are equivalent to Pages — their advantage is SPA routing, which you don't need. Migrating = effort for zero gain.
- **AWS (S3+CloudFront) is the wrong tool** — most ops-heavy option, and "free" only for the first 12 months then it's metered. Bad fit. (Save the AWS energy for the DVA-C02 labs.)

So: **one repo, several `.html` files.** That's what this folder is.

### The repo choice is genuinely yours (two good options)

**Option A — minimal friction (reuse the existing repo).** Keep `an0nya.github.io/RYS-vivisection-experiments/`. Move its current `index.html` → `gemma.html`, drop in the new `index.html` + `granite.html` + `hrm.html` + `assets/`. History preserved; the Gemma page just moves down one level.
- *Downside:* the repo name still says "RYS," which now undersells the work (granite vivisection is steering/noise, HRM is recurrent — broader than RYS).

**Option B — the self-branding play (a user site).** Make `an0nya.github.io` (the root user site) the portfolio hub. URL becomes `an0nya.github.io/` for the hub, `/granite.html` etc. Strongest front-door for the social-media/portfolio streak you mentioned.
- *Downside:* the Gemma page's existing URL changes (any links you've shared break), and it's a bit more setup.

I built the draft to work for **either** without changes. My lean: **Option B** if you care about the portfolio/streak (a root-domain hub is the move); **Option A** if you just want it live tonight. This is the kind of call the publishing memory says is yours, so I left it for you.

### Deploy steps (GUI-first, since terminal is not your happy place)

**Option A, via GitHub web UI (no terminal):**
1. Go to your `RYS-vivisection-experiments` repo on github.com.
2. Rename the existing `index.html` → `gemma.html` (open it → pencil/edit → the rename field is the filename box at top → commit).
3. Upload the new files: "Add file → Upload files," drag in `index.html`, `granite.html`, `hrm.html`, and the `assets/` folder. Commit.
4. Pages redeploys automatically in ~1 min. Done.

**If you'd rather I script the git for Option A or B,** say so in the morning — I'll give you exact copy-paste commands (or just do it, with your ok). I didn't push anything tonight because deploying/renaming a live repo is your call to make awake.

---

## What I added to the science (the part that wasn't done yet)

Your granite **overnight sweep is still running** (I first analyzed a mid-run snapshot at config 372 and wrongly called it "expired" — it wasn't; it's at ~402/469 and grinding through the multi-layer combos, interference-prune, and damping rounds, ETA ~2h). I analyzed the snapshot (`rys-tools/granite/analyze_overnight.py`, output saved to `rys-tools/granite/results/overnight_analysis.txt`) and **rewrote §9 of `granite_sweep_writeup.md`** with real verdicts for everything that's landed. The damping verdicts will fold in when the run finishes. New findings so far, all on the granite page:

1. **New champion: `combo_10_38`** — EQ 0.769 (paired t = **+9.38**) with MC **pristine at 1.000**. It beats *every single layer* (best single was dup_10 at +8.98) and beats it *cleanly* — dup_38 alone dents MC, but in combination the cost vanishes. **Cross-depth EQ-booster pairs stack superadditively.** This is the direct granite analog of your Gemma "cross-zone amplification" finding.
2. **Granite reproduces the Gemma archetype split.** Combos are either *generalists* (EQ↑, MC held: built from L10/17/29) or *EQ-specialists* (EQ↑, MC paid: anything containing L33). Same three-archetype story as E4B, surfaced through duplication instead of pruning.
3. **Dose-response = a clean monotonic ceiling.** For every winner layer, **×2 is the therapeutic peak; ×3 declines; ×4+ collapses EQ and MC to the floor.** The lethal dose sits just past the therapeutic one — exactly what "dup = power-iteration toward a collapse attractor" predicts. **One exception:** L24's ×3 genuinely beats its ×2 (flagged on the chart).
4. **Math stays floored** (42/372 configs nudge a single probe; no real arithmetic gain) — confirms the saturation prediction.

The two granite SVG figures (layer map, dose-response) are generated straight from the JSONL — rerun `assets/make_granite_figs.py` if the data changes.

---

## Figures: what's done vs what you might want to build

| figure | page | status |
|---|---|---|
| Granite **layer map** (dup/prune EQ per layer) | granite | ✅ generated from data, SVG, on-brand, dark-mode-aware |
| Granite **dose-response** | granite | ✅ generated from data, SVG |
| HRM **depth geometry** | hrm | ⚠️ existing matplotlib PNG, *framed* (light card on dark). Legible but doesn't match the hand-drawn SVG look. |
| HRM **decoupling scatter** | hrm | ⚠️ same — existing PNG, framed. It's the right figure and reads well; just a different visual register. |
| **Combo table** (combo_10_38 etc.) | granite | ✅ as an HTML table |
| Gemma figures | gemma | ✅ untouched (your originals) |

**If you want the HRM figures to match** the hand-built SVG style of the rest: the data is all in `HRM-mlx/figs/*.json` (battery + interlingua per config). I can write an SVG generator like `make_granite_figs.py` to redraw the decoupling scatter and depth scan. Didn't do it tonight because (a) HRM is your "maybe leave as draft" pile and (b) the framed PNGs are honest and legible. **Say the word and it's ~30 min.**

**Optional hub teasers:** the landing page cards are text-forward (no thumbnails). If you want little chart thumbnails on each card, I can crop/generate them. Left them clean for now.

---

## Things you flagged-then-forgot, or that I noticed (your "what did we miss" ask)

1. **The granite damping / interference-prune / rescue rounds are running right now** (I'd mistakenly written them off as never-run; the sweep is alive and into them as of ~402/469). They'll produce verdicts within ~2h — I'll fold them into the writeup §9 and the granite page when done. **The dose-response makes the damping round the one to watch:** is the therapeutic window *wider in α (damping) than in integer copies*? i.e. can a damped 1.5-copy of L10 beat the ×2 ceiling without the ×3 collapse? (The granite page §8 is marked "running now" with that question front and center.)
2. **The Gemma 31B sweep stalled/errored — I don't think you noticed.** `gemma_31b_nocot_results.jsonl` is only 8.6 KB (vs 18 MB for E4B) and there are `.bak-error` files. Memory says it was "ready to run after the 7pm reset" and the `dup_2` de-risk passed — but the actual sweep crashed early. **This is the headline-grade result if you can land it** ("did the RYS-on-31B surgery the technique's own author said he never got to"). Worth debugging the stall. Right now the site treats 31B as geometry-only (which matches the live page).
3. **HF cache is 22 GB on your boot drive** (`~/.cache/huggingface/hub`, internal SSD at ~83% full). Flagged in the granite session ("want a spawned task to migrate it?") and never resolved. Set `HF_HOME` to the NVMe and move it — but not mid-anything, since it'll break `load()` paths.
4. **Seed-packing optimization** — greenlit, still just a comment in `granite_mlx_sweep.py`. ~4 GB headroom exists; would cut sweep time meaningfully on the next run.
5. **Granite combos were pairs only** — no triples/quads/kitchen-sink (your plan mentioned them; only pairs ran before the block died). Dose-response predicts *same-layer* triples overdose, but *cross-layer* triples (e.g. `combo_10_24_38`) are untested and might stack further. Clean follow-up.
6. **`eq_sketch` grader isn't human-validated** (same caveat as Gemma). The EQ *rankings* are trustworthy; the absolute numbers aren't. If you ever publish "EQ improved by N%," validate against real EQ-Bench reference data first. I kept all EQ claims as relative/directional on the page.
7. **Your live Gemma page still has its pending TODO** (relocate the §9 inline scan figure into Appendix G). I copied the page verbatim, so that TODO is unchanged. Not touched.

---

## Voice / tone choices I made (so you can override)

- Matched the Gemma page's literary-clinical register ("the patient," "specimen," section §-numbers, deks). The granite + HRM prose is lifted/tightened from your own writeups, which were already in that voice.
- **Credited David Ng respectfully** per the publishing memory — RYS = "Repeat Your Self" (the correct expansion), his partial-credit probe design framed as elegant-and-extended, not naive-and-debunked. The hub colophon cites his "every architecture has its own neuroanatomy" line and the convergence with your archetype split. No snark. (Double-check the *copied* gemma.html for any old "Repeat Yourself, Stupid" / tropical-island snark — the live page was supposedly de-snarked 2026-05-29, but verify.)
- **HRM is badged DRAFT** (gold dashed banner up top + the hub card) per your "might not be ready / don't fully understand it" note. The framing leans into that — it's published *as* an honest negative result + methodology lesson, which is arguably its strongest form. If you'd rather it not be linked publicly yet, just delete the `hrm.html` link from `index.html` and the nav; the page stays as a private draft.

---

## Quick local preview

A static server is registered in `.claude/launch.json` (also at `~/.claude/launch.json` for the preview tool). If the preview isn't up:
```
python3 -m http.server 8013 --directory /Users/anya/Projects/vivisection-site
```
then open http://localhost:8013. Or just double-click `index.html` — it's all relative paths, works from `file://` too (the Google Fonts need network, but everything else is local).

---

## My recommended next moves (in order)

1. **Skim the three new pages** in the browser; mark anything in the prose you want changed (you said you'd spot-edit — the HTML is hand-readable).
2. **Pick the repo option (A or B)** and either deploy via the web UI or tell me to script it.
3. **Decide HRM: publish-as-draft or keep private** (one-link delete either way).
4. *(Later, real science)* run the **granite damping round** — the dose-response made it the obvious next experiment — and **debug the 31B stall**, which is the biggest potential headline.
