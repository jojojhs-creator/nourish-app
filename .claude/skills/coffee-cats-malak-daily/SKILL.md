---
name: coffee-cats-malak-daily
description: Generate the next Coffee, Cats & Malak daily episode (1 × 15s animated clip + thumbnail) and trigger auto-posting to YouTube and TikTok. Use when the user says "CCM day X", "next episode", or asks to produce/post a new Coffee, Cats & Malak episode.
---

# Coffee, Cats & Malak — Daily Episode

Produces one episode end-to-end and hands off to the auto-posting GitHub Actions workflow.

## Steps

1. **Check credits first** — call `balance`. Then call `generate_video(get_cost: true)`
   and `generate_image(get_cost: true)` to preflight costs. Log both to the user.
   Only proceed if credits clearly cover the run (expect ~24.5 credits total).

2. **Pick the scenario** — read `docs/CoffeeCatsMalak_Content_Calendar.md` and find
   the next entry not yet marked Done (or use the day number given by the user).

3. **Follow `docs/COFFEE_CATS_MALAK_RUNBOOK.md`** step by step:
   - Generate 1 × 15s clip via Higgsfield (Seedance 2.0 FAST, 9:16, 480p; embed
     character element IDs from the runbook's ID table)
   - Generate 1 × thumbnail via Higgsfield nano_banana_pro
   - Write `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`

4. **Trigger posting** — use `mcp__github__actions_run_trigger` (method: `run_workflow`,
   workflow_id: `storyowl-autopost.yml`, ref: `main`) with:
   - `video_url`: the raw Higgsfield CloudFront URL from the clip generation
   - `thumbnail_url`: the raw Higgsfield CloudFront URL from the thumbnail generation
   - `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`

   No Cloudinary upload, no ffmpeg merge — post the Higgsfield URL directly.

5. **Update progress** — mark the episode Done in `docs/CoffeeCatsMalak_Content_Calendar.md`.

6. **Report back** — the scenario title, Higgsfield video URL, and confirm the
   `run_workflow` call succeeded so the user can check the Actions run.

## Notes

- Never use `generate_audio: false` — omit it entirely so Seedance bakes in ambient audio.
- Never add on-screen text or captions to prompts.
- Always embed all relevant character element IDs in the prompt using `<<<element_id>>>` syntax.
- If a character isn't in a given scenario, don't embed their element ID.
- TikTok posts in DRAFT mode by default — caption must be pasted manually in the TikTok app.
