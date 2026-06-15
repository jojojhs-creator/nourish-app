# nourish-app

Repo root is mostly a static site (`index.html`, `storyowl-privacy.html`,
`storyowl-terms.html`). The active project is **StoryOwl**, an automated bedtime-story
Shorts/TikTok channel.

## StoryOwl automation overview

Two-tier pipeline that produces and posts one ~60s bedtime-story episode per day:

- **Tier 1 (generation)** - runs inside an agent session via the `/storyowl-daily`
  skill (`.claude/skills/storyowl-daily/SKILL.md`), following
  `docs/STORYOWL_RUNBOOK.md`:
  1. Pick the next episode from `docs/StoryOwl_60_Day_Plan.md` (alternates EN/AR).
  2. Write a clip-by-clip script (EN voice "Olivia", AR voice "Nour" - AR script must
     have full tashkeel/diacritics).
  3. Generate 4 video clips (Higgsfield Seedance 2.0 FAST, 9:16, 480p; clips 1 & 4 use
     the saved "StoryOwl" reference element).
  4. Generate voiceover (Higgsfield inworld TTS) + thumbnail (nano_banana_2).
  5. Upload all 6 assets to Cloudinary as `storyowl_ep<X>_clip1-4`, `_voice`, `_thumb`,
     then run a `transform-asset` merge -> final MP4 URL.
  6. Write `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`.
  7. Fire a `repository_dispatch` (`storyowl_video_ready`) with `video_url`,
     `thumbnail_url`, and the metadata above.
  8. Mark the episode `Done` in `docs/StoryOwl_60_Day_Plan.md`.

- **Tier 2 (posting)** - `.github/workflows/storyowl-autopost.yml` +
  `scripts/storyowl/orchestrator.py`. Downloads the video (and thumbnail), then:
  - **YouTube**: `youtube_uploader.py` posts as a public, Made-for-Kids Short and sets
    the custom thumbnail via `thumbnails().set()` (requires phone-verified channel;
    best-effort, won't fail the run).
  - **TikTok**: `tiktok_uploader.py` posts per the `TIKTOK_POST_MODE` repo variable
    (`DRAFT` / `SELF_ONLY` / `PUBLIC_TO_EVERYONE`).
  - Falls back to dry-run per platform if that platform's secrets aren't configured.
  - Writes `out/result.json` + a `$GITHUB_STEP_SUMMARY` table.

Full setup/credentials/troubleshooting: `docs/STORYOWL_SETUP.md`.

## Known platform limitations

- **TikTok caption in `DRAFT` mode**: TikTok's inbox-init API does not accept
  `post_info`, so `tiktok_caption` can't be attached to draft/inbox uploads - this is a
  TikTok API limitation, not a bug. The caption is generated and shown in the Actions
  job summary for manual copy/paste when finishing the post in the TikTok app. Once
  `TIKTOK_POST_MODE` is `SELF_ONLY`/`PUBLIC_TO_EVERYONE` (Direct Post, requires TikTok
  Content Posting API audit approval), the caption + a video-frame cover
  (`video_cover_timestamp_ms`) are set automatically.
- **YouTube custom thumbnails**: require the channel to be phone-verified
  ("Feature eligibility"). If not verified, `thumbnails().set()` errors but the video
  upload itself still succeeds.

## Daily automation

For a fully unattended daily run at 9am: set up a Claude Code scheduled
trigger/routine (claude.ai/code -> repo -> scheduled triggers) that runs
`/storyowl-daily` once per day. Each run generates the episode and fires
`repository_dispatch` itself, which triggers Tier 2 posting automatically. For TikTok
to post **publicly** (not just to inbox), `TIKTOK_POST_MODE` must be
`PUBLIC_TO_EVERYONE` (needs TikTok's Content Posting API audit approval).

## Progress

Episodes 1-3 generated and posted (see `docs/StoryOwl_60_Day_Plan.md` for status):
1. "Luna the Sleepy Bunny" (EN)
2. "النجمة الصغيرة" / The Little Star (AR)
3. "Theo's Quiet Night" (EN)

All three were posted to TikTok in `DRAFT` mode (inbox, no caption attached) -
captions need to be pasted manually when finishing those posts in the TikTok app.
