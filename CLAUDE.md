# nourish-app

Repo root is mostly a static site (`index.html`, `storyowl-privacy.html`,
`storyowl-terms.html` — legal pages, filenames kept stable since they're already
registered as the privacy/terms URLs on the TikTok/YouTube app consoles). The active
project is **Coffee, Cats & Malak**, an automated Shorts/TikTok channel: daily
slice-of-life clips of Malak and her three cats — Olive, Mocha, and Sky — in their
apartment (mornings, cooking, balcony city views, cat chaos). See
`docs/CoffeeCatsMalak_Content_Calendar.md` for the scenario calendar.

> Formerly "StoryOwl" (bedtime-story episodes with an owl mascot) — same YouTube/TikTok
> accounts, fully rebranded to this new character-driven format. Historical StoryOwl
> episodes are not part of this content line going forward.

## Coffee, Cats & Malak automation overview

Two-tier pipeline that produces and posts one 15-30s daily-life clip per day:

- **Tier 1 (generation)** - runs inside an agent session via the
  `/coffee-cats-malak-daily` skill (`.claude/skills/coffee-cats-malak-daily/SKILL.md`),
  following `docs/COFFEE_CATS_MALAK_RUNBOOK.md`:
  1. Pick the next scenario from `docs/CoffeeCatsMalak_Content_Calendar.md`.
  2. Write the scene beat(s) for a single 15s clip, or two 15s clips for a 30s scene.
  3. Generate the clip(s) via Higgsfield Seedance 2.0 FAST (9:16, 480p), embedding the
     Malak/Olive/Mocha/Sky reference elements as needed for the scene. Audio is
     **not** disabled — omit `generate_audio` entirely so Seedance bakes in matching
     ambient sound/music (same rule as the hype-clip workflow below). No dialogue, no
     on-screen captions.
  4. Generate a thumbnail (Higgsfield nano_banana_2).
  5. **Single-clip (15s) scenes**: skip Cloudinary entirely - post straight from
     Higgsfield's own clip URL via `mcp__github__actions_run_trigger` (workflow:
     `storyowl-autopost.yml`) with `video_url` = the Higgsfield clip URL.
  6. **Two-clip (30s) scenes**: trigger `storyowl-merge-and-post.yml` with `clip1_url` +
     `clip2_url` only (`clip3_url`/`clip4_url`/`voice_url` stay empty) - it ffmpeg-concats
     the two clips back-to-back, keeping each clip's own baked-in audio. No voiceover
     track is generated or needed for this format.
  7. Write `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`
     (the on-screen video never has burned-in captions, but the TikTok post's caption/
     hashtag text is still generated as normal platform metadata).
  8. Mark the scenario `Done` in `docs/CoffeeCatsMalak_Content_Calendar.md`.

- **Tier 2 (posting)** - `.github/workflows/storyowl-autopost.yml` (single finished
  video) or `.github/workflows/storyowl-merge-and-post.yml` (two clips, ffmpeg
  concat) + `scripts/storyowl/orchestrator.py`. Downloads the video (and thumbnail),
  then:
  - **YouTube**: `youtube_uploader.py` posts as a public Short and sets the custom
    thumbnail via `thumbnails().set()` (requires phone-verified channel; best-effort,
    won't fail the run).
  - **TikTok**: `tiktok_uploader.py` posts per the `TIKTOK_POST_MODE` repo variable
    (`DRAFT` / `SELF_ONLY` / `PUBLIC_TO_EVERYONE`).
  - Falls back to dry-run per platform if that platform's secrets aren't configured.
  - Writes `out/result.json` + a `$GITHUB_STEP_SUMMARY` table.

Full setup/credentials/troubleshooting: `docs/COFFEE_CATS_MALAK_SETUP.md`.

## The cast

- **Malak** - real person (consent given for an animated/stylized likeness, not a
  photorealistic deepfake), brunette, tall. Character reference element built from her
  own photo. Visual style: semi-realistic 3D/CGI (Pixar-adjacent), cozy apartment,
  warm morning light, city-skyline window backdrop - matches the `oopsyvibes`-style
  reference the channel is modeled on.
- **Olive** - Bengal/Tabby mix. The mischievous one (knocks things over, steals food,
  3am zoomies).
- **Mocha** - Golden Chinchilla Scottish Fold. The cozy/fluffy one (grooming rituals,
  dramatic naps).
- **Sky** - White Persian with heterochromia (one blue eye, one green/gold eye). The
  diva (sunbeam naps, "photoshoot" poses, picky about treats).

All four have their own Higgsfield reference element so they stay visually consistent
across every clip - same mechanism the old StoryOwl mascot element used, just four
characters instead of one.

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

For a fully unattended daily run: set up a Claude Code scheduled trigger/routine
(claude.ai/code -> repo -> scheduled triggers) that runs `/coffee-cats-malak-daily`
once per day. Each run generates the clip(s) and posts via the workflows above. For
TikTok to post **publicly** (not just to inbox), `TIKTOK_POST_MODE` must be
`PUBLIC_TO_EVERYONE` (needs TikTok's Content Posting API audit approval).

## Rebrand notes (account-level, manual, not automatable)

Renaming the actual YouTube/TikTok account, uploading the new profile photo, and
setting the new bio are **not** handled by any script or MCP tool here - neither
platform's API exposes profile/identity editing to this pipeline. These must be done
manually in YouTube Studio and the TikTok app:

- **Name**: Coffee, Cats & Malak
- **Bio**: "One girl, three cats, zero peace and quiet ☕😹"
- **Profile photo**: generate via Higgsfield (portrait crop of Malak's reference
  element) and upload manually once credits allow generation.

## Hype clips (standalone engagement content)

Separate from daily scenario posts - short viral-style clips to grow followers.

**Rules (enforced — do not break):**
- **One clip per hype post** — never batch 3 and post them separately in one session.
- **15 seconds**, `9:16`, Seedance 2.0 FAST.
- **`generate_audio: false` is NOT used here** — these clips need Seedance's
  auto-generated beat. Omit `generate_audio` entirely so Seedance bakes in matching
  music.
- **Describe the rhythm in the prompt** — e.g. "dancing perfectly in sync to a hard EDM
  drop beat", "bouncing to a viral tropical house rhythm". This steers Seedance's music.
- **Post via `storyowl-autopost.yml`** using the Higgsfield CloudFront URL directly
  (no Cloudinary upload needed for hype clips) - the same no-Cloudinary path the daily
  single-clip scenario posts now use too.

## Progress

Rebrand in progress (see `docs/CoffeeCatsMalak_Content_Calendar.md` for scenario
status). No Coffee, Cats & Malak clips generated yet - blocked on:
1. Higgsfield credit top-up (balance was near zero as of the last generation attempt).
2. Building the four character reference elements (Malak, Olive, Mocha, Sky) from
   their reference photos.
3. Manually renaming the account / uploading the new profile photo + bio on
   YouTube and TikTok.

Prior StoryOwl bedtime-story episodes (1-4b) were posted under the old format; that
calendar (`docs/StoryOwl_60_Day_Plan.md`) is retired and superseded by
`docs/CoffeeCatsMalak_Content_Calendar.md`.

TikTok posts in `DRAFT` mode — captions must be pasted manually in the TikTok app.
