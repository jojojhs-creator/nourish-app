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

2. **Pick the scenario — check ALL branches first (duplicate protection).**
   Runs before you may have marked episodes Done on `claude/`-prefixed branches
   without reaching main. Before picking, run:
   `git fetch origin '+refs/heads/claude/*:refs/remotes/origin/claude/*'` and check
   the calendar file on every `origin/claude/*` branch whose latest commit is newer
   than main's. An episode marked Done on ANY branch counts as Done. Then pick the
   next episode not marked Done anywhere. NEVER produce an episode that any branch
   already shows as Done — a duplicate post is worse than a skipped run.

3. **Follow `docs/COFFEE_CATS_MALAK_RUNBOOK.md` step by step — ORDER MATTERS:**
   - FIRST generate the SETUP keyframe image via nano_banana_pro (the scenario's
     calm beat-1 moment with mischief visibly imminent — NEVER the payoff moment;
     element IDs + mandatory style block). This one image is also the thumbnail —
     never generate a second image.
   - When Malak appears, ALWAYS pass the canonical Malak portrait
     (`medias: [{value: "7c8a4bde-3c17-4257-80f3-b8864f5a1ea9", role: "image"}]`)
     and include the runbook's Malak-match sentence — she is the main character
     and must look identical in every episode.
   - THEN generate the 15s clip via Seedance 2.0 FAST (9:16, 480p, `genre: "comedy"`)
     passing the keyframe job ID as `medias: [{value: <keyframe_job_id>, role:
     "start_image"}]`, with a second-by-second script prompt (Seconds 0-3 / 3-7 /
     7-11 / 11-15 beats) per the runbook's proven example.
   - Write `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`

4. **Trigger posting** — use `mcp__github__actions_run_trigger` (method: `run_workflow`,
   workflow_id: `storyowl-autopost.yml`, ref: `main`) with:
   - `video_url`: the raw Higgsfield CloudFront URL from the clip generation
   - `thumbnail_url`: the raw Higgsfield CloudFront URL from the thumbnail generation
   - `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`

   No Cloudinary upload, no ffmpeg merge — post the Higgsfield URL directly.

5. **Update progress** — mark the episode Done (with the clip URL) in
   `docs/CoffeeCatsMalak_Content_Calendar.md`, commit, and push to `main`. If the
   push to main is rejected, push your branch AND clearly state in your final
   summary that main was not updated and the branch-push permission needs enabling.

6. **Report back** — the scenario title, Higgsfield video URL, and confirm the
   `run_workflow` call succeeded so the user can check the Actions run.

## Notes

- Follow the calendar row's **Energy** column: `Chaotic` episodes use the runbook's
  3-beat structure (calm setup → escalating repeated actions → big exaggerated Pixar
  reaction payoff). `Cozy` episodes are slow and warm with one small comedic surprise.
  Never write a single-action prompt — chaotic scenes need 2–4 escalating actions.
- **Every prompt (clip AND thumbnail) must end with the runbook's mandatory style
  block** ("Fully stylized Pixar/Disney 3D cartoon animation... NOT photorealistic...").
  Never use just "Pixar/CGI animated style" alone — it drifts photorealistic.
- Never use `generate_audio: false` — omit it entirely so Seedance bakes in ambient audio.
- Never add on-screen text or captions to prompts.
- Always embed all relevant character element IDs in the prompt using `<<<element_id>>>` syntax.
- If a character isn't in a given scenario, don't embed their element ID.
- TikTok posts in DRAFT mode by default — caption must be pasted manually in the TikTok app.
