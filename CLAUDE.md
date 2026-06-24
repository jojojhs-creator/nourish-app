# nourish-app

Repo root is mostly a static site (`index.html`, `storyowl-privacy.html`,
`storyowl-terms.html`). The active project is **StoryOwl**, an automated kids
Shorts/TikTok channel — bedtime stories, fables, educational shorts, adventure
micro-stories, funny kids stories, and cultural folklore (see content categories in
`docs/StoryOwl_60_Day_Plan.md`).

## StoryOwl automation overview

Two-tier pipeline that produces and posts one ~60s bedtime-story episode per day:

- **Tier 1 (generation)** - runs inside an agent session via the `/storyowl-daily`
  skill (`.claude/skills/storyowl-daily/SKILL.md`), following
  `docs/STORYOWL_RUNBOOK.md`:
  1. Pick the next episode from `docs/StoryOwl_60_Day_Plan.md` (alternates EN/AR).
  2. Write a clip-by-clip script (EN voice "Olivia", AR voice "Nour" - AR script must
     have full tashkeel/diacritics).
  3. Generate 4 video clips (Higgsfield Seedance 2.0 FAST, 9:16, 480p, `generate_audio: false`;
     clips 1 & 4 use the saved "StoryOwl" reference element; all 4 clips must be unique scenes).
  4. Generate voiceover (Higgsfield inworld TTS) + thumbnail (nano_banana_2).
  5. Upload all 6 assets to Cloudinary as `storyowl_ep<X>_clip1-4`, `_voice`, `_thumb`.
  6. Write `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`.
  7. Use `mcp__github__actions_run_trigger` (method: `run_workflow`, workflow:
     `storyowl-merge-and-post.yml`, ref: `main`) with `clip1_url`–`clip4_url`,
     `voice_url`, `thumbnail_url`, and the metadata above. This workflow ffmpeg-merges
     the clips + overlays the voice on GitHub Actions runners (Cloudinary `fl_splice`
     does not work on this account). No `GITHUB_PAT` needed.
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

## Hype clips (standalone engagement content)

Separate from episodes — short viral-style clips to grow followers between story posts.

**Rules (enforced — do not break):**
- **One clip per hype post** — never batch 3 and post them separately in one session.
- **15 seconds**, `9:16`, Seedance 2.0 FAST.
- **`generate_audio: false` is NOT used here** — these clips need Seedance's
  auto-generated beat. Omit `generate_audio` entirely so Seedance bakes in matching music.
- **Describe the rhythm in the prompt** — e.g. "dancing perfectly in sync to a hard EDM
  drop beat", "bouncing to a viral tropical house rhythm". This steers Seedance's music.
- **Content**: dancing animals (cat, dog, bunny, etc.) or a clearly cartoon/animated
  child character. Never use "baby" or "infant" keywords — they trigger NSFW filters.
  Use "cartoon child character", "kawaii character", "chibi character" instead.
- **Post via `storyowl-autopost.yml`** using the Higgsfield CloudFront URL directly
  (no Cloudinary upload needed for hype clips).

## Cloudinary merge workaround

`fl_splice` transformations do not work on this Cloudinary account. Always use
`storyowl-merge-and-post.yml` (ffmpeg on GitHub Actions) to concatenate clips.
Pass individual clip URLs as `clip1_url`–`clip4_url` + `voice_url`. All 4 clip
URLs must be **unique** — never reuse the same URL in two positions.

## Progress

Episodes 1–4b generated and posted (see `docs/StoryOwl_60_Day_Plan.md` for status):
1. "Luna the Sleepy Bunny" (EN)
2. "النجمة الصغيرة" / The Little Star (AR)
3. "Theo's Quiet Night" (EN)
4. "القمر وسامي" / The Moon and Sami (AR)
4b. "الأسد والفأر" / The Lion and the Mouse (AR Fable)

TikTok posts in `DRAFT` mode — captions must be pasted manually in the TikTok app.
