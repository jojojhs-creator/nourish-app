# Coffee, Cats & Malak Daily Post

Produces one Coffee, Cats & Malak daily-life clip end-to-end and hands off to the
auto-posting GitHub Actions workflow.

## Steps

1. **Pick the scenario**: read `docs/CoffeeCatsMalak_Content_Calendar.md` and find the
   next entry not yet marked done (or use the day number given by the user, e.g.
   "Coffee Cats Malak day 5").
2. **Follow `docs/COFFEE_CATS_MALAK_RUNBOOK.md`** step by step:
   - Write the scene beat(s) — a single 15s clip, or two 15s clips for a 30s scene
   - Generate the clip(s) via Higgsfield (Seedance 2.0 FAST, 9:16, 480p; embed the
     Malak/Olive/Mocha/Sky reference element IDs from the runbook as the scene calls
     for; omit `generate_audio` so Seedance bakes in ambient sound/music — no dialogue,
     no on-screen captions)
   - Generate the thumbnail via Higgsfield nano_banana_2
   - **Single-clip scenes**: skip Cloudinary — trigger `storyowl-autopost.yml` directly
     with the Higgsfield clip URL as `video_url`
   - **Two-clip scenes**: trigger `storyowl-merge-and-post.yml` with `clip1_url` +
     `clip2_url` only (leave `clip3_url`/`clip4_url`/`voice_url` empty)
   - Write `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`
3. **Trigger posting**: use the `mcp__github__actions_run_trigger` tool (method:
   `run_workflow`, ref: `main`) — see `docs/COFFEE_CATS_MALAK_RUNBOOK.md` step 6 for the
   exact call and which workflow_id to use for single vs. two-clip scenes. The GitHub
   MCP connector is already authenticated; no `GITHUB_PAT` environment variable is
   needed.
4. **Update progress**: mark the scenario as done in
   `docs/CoffeeCatsMalak_Content_Calendar.md`.
5. Report back: the scenario title, the video URL(s) used, and confirm the workflow
   trigger succeeded (so the user can check the Actions run for YouTube/TikTok posting
   status).

## Notes

- The four character reference elements (Malak, Olive, Mocha, Sky) must exist before
  this skill can run — see `docs/COFFEE_CATS_MALAK_RUNBOOK.md` for how they were built
  and where their element IDs are recorded. If any are missing, stop and say so rather
  than generating without character consistency.
- Malak is a real person; the animated likeness is used with her explicit consent.
  Keep the visual style stylized/animated (Pixar-adjacent 3D), never photorealistic.
- No dialogue and no on-screen burned-in captions in any clip. Silent/ambient audio
  with occasional light vocal reactions (sighs, an annoyed "hmph", cat chirps/meows) is
  fine since Seedance bakes those in — just describe the reaction in the prompt, don't
  request spoken lines.
- If the user just says "Coffee Cats Malak day X" without further detail, use the
  calendar entry for day X as-is; don't ask for confirmation on every creative detail -
  use good judgment consistent with prior scenarios' cozy, lighthearted tone.
- In `DRAFT` mode, TikTok doesn't accept a caption via the API - the generated
  `tiktok_caption` is shown in the Actions job summary for manual copy/paste when
  finishing the post in the TikTok app. Once `TIKTOK_POST_MODE` is `SELF_ONLY` or
  `PUBLIC_TO_EVERYONE`, the caption (and a video-frame cover image) are set
  automatically.
