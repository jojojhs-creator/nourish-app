---
name: storyowl-daily
description: Generate the next StoryOwl bedtime-story episode (script, video clips, voiceover, thumbnail, Cloudinary merge, and platform metadata) and trigger auto-posting to YouTube and TikTok. Use when the user says "StoryOwl day X", "next StoryOwl episode", or asks to produce/post a new StoryOwl episode.
---

# StoryOwl Daily Episode

Produces one StoryOwl episode end-to-end and hands off to the auto-posting GitHub
Actions workflow.

## Steps

1. **Pick the episode**: read `docs/StoryOwl_60_Day_Plan.md` and find the next entry not
   yet marked done (or use the day number given by the user, e.g. "StoryOwl day 5").
2. **Follow `docs/STORYOWL_RUNBOOK.md`** step by step:
   - Write the script (clip-by-clip; full tashkeel if Arabic)
   - Generate the 4 video clips via Higgsfield (Seedance 2.0 FAST, 9:16, 480p; clips 1
     & 4 use the "StoryOwl" reference element)
   - Generate the voiceover via Higgsfield inworld TTS (Olivia EN / Nour AR)
   - Generate the thumbnail via Higgsfield nano_banana_2
   - Upload all 6 assets to Cloudinary with consistent `storyowl_ep<X>_*` names
     (including the thumbnail as `storyowl_ep<X>_thumb`)
   - Run the Cloudinary `transform-asset` merge to get the final MP4 URL
   - Write `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`
3. **Trigger posting**: POST to `repository_dispatch` (event type
   `storyowl_video_ready`) with the final video URL, the thumbnail URL, and the step-2
   metadata, per the `curl` example in `docs/STORYOWL_RUNBOOK.md` step 8 (includes
   `thumbnail_url`, which becomes the YouTube custom thumbnail). This requires a GitHub
   PAT with `repo` scope (or fine-grained "Contents: read & write" + "Actions: write" for
   this repo) - ask the user for `GITHUB_PAT` if it isn't already available in the
   environment.
4. **Update progress**: mark the episode as done in `docs/StoryOwl_60_Day_Plan.md`.
5. Report back: the episode title/language, the Cloudinary video URL, and confirm the
   `repository_dispatch` call succeeded (so the user can check the Actions run for
   YouTube/TikTok posting status).

## Notes

- If the user just says "StoryOwl day X" without further detail, use the plan entry for
  day X as-is; don't ask for confirmation on every creative detail - use good judgment
  consistent with prior episodes' tone (gentle, calm, bedtime-appropriate).
- Until TikTok's Content Posting API is approved for this account, posting happens in
  whatever mode `TIKTOK_POST_MODE` is set to (see `docs/STORYOWL_SETUP.md`) - draft/inbox
  by default, so don't be alarmed if TikTok doesn't show as "published" yet.
- In `DRAFT` mode, TikTok doesn't accept a caption via the API - the generated
  `tiktok_caption` is shown in the Actions job summary for manual copy/paste when
  finishing the post in the TikTok app. Once `TIKTOK_POST_MODE` is `SELF_ONLY` or
  `PUBLIC_TO_EVERYONE`, the caption (and a video-frame cover image) are set
  automatically.
