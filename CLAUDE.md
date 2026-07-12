# nourish-app

Repo root is mostly a static site (`index.html`, `storyowl-privacy.html`,
`storyowl-terms.html`). The active project is **Coffee, Cats & Malak**, an automated
daily animated short-form channel (YouTube Shorts + TikTok) — one girl, three cats,
zero peace and quiet. Slice-of-life comedy/cozy content in Pixar/CGI animation style.

## Coffee, Cats & Malak — automation overview

Two-tier pipeline that produces and posts one 15-second animated episode per day:

- **Tier 1 (generation)** — runs inside an agent session via the `/coffee-cats-malak-daily`
  skill (`.claude/skills/coffee-cats-malak-daily/SKILL.md`), following
  `docs/COFFEE_CATS_MALAK_RUNBOOK.md`:
  1. Check credits: call `balance` + `generate_video(get_cost: true)` before every run.
  2. Pick the next scenario from `docs/CoffeeCatsMalak_Content_Calendar.md`.
  3. Generate 1 × 15s clip (Higgsfield Seedance 2.0 FAST, 9:16, 480p; embed character
     element IDs from the runbook; omit `generate_audio` entirely).
  4. Generate thumbnail (Higgsfield nano_banana_pro).
  5. Write `youtube_title`, `youtube_description`, `youtube_tags`, `tiktok_caption`.
  6. Use `mcp__github__actions_run_trigger` (method: `run_workflow`, workflow:
     `storyowl-autopost.yml`, ref: `main`) with `video_url` (raw Higgsfield CloudFront
     URL), `thumbnail_url`, and the metadata. No Cloudinary upload needed.
  7. Mark the scenario `Done` in `docs/CoffeeCatsMalak_Content_Calendar.md`.

- **Tier 2 (posting)** — `.github/workflows/storyowl-autopost.yml` +
  `scripts/storyowl/orchestrator.py`. Downloads the video (and thumbnail), then:
  - **YouTube**: `youtube_uploader.py` posts as a public Short and sets the custom
    thumbnail via `thumbnails().set()` (requires phone-verified channel; best-effort).
  - **TikTok**: `tiktok_uploader.py` posts per the `TIKTOK_POST_MODE` repo variable
    (`DRAFT` / `SELF_ONLY` / `PUBLIC_TO_EVERYONE`).
  - Falls back to dry-run per platform if that platform's secrets aren't configured.
  - Writes `out/result.json` + a `$GITHUB_STEP_SUMMARY` table.

Full setup/credentials/troubleshooting: `docs/COFFEE_CATS_MALAK_SETUP.md`.

## The Cast

| Character | Description | Personality |
|---|---|---|
| **Malak** | Brunette, dark wavy hair, brown eyes, olive skin | The human — relatable, always slightly overwhelmed |
| **Mocha** | Golden Scottish Fold, folded ears, yellow-green eyes | Dramatic — steals warm spots, grooming rituals |
| **Sky** | White fluffy kitten, blue eyes | Chaotic — gets into everything, very curious |
| **Olive** | Classic tabby, striped, sleepy expression | Unbothered — naps anywhere, judges everyone |

## Character Reference Element IDs (Higgsfield)

| Character | Element ID |
|---|---|
| Malak | TBD — update after one-time setup session |
| Mocha | TBD — update after one-time setup session |
| Sky | TBD — update after one-time setup session |
| Olive | TBD — update after one-time setup session |

Embed in prompts as `<<<element_id>>>`. See `docs/COFFEE_CATS_MALAK_RUNBOOK.md`.

## Credit check rule

**Before every `generate_video` or `generate_image` call:**
1. Call `balance` — log current credits
2. Call with `get_cost: true` — log exact cost
3. Only proceed if balance clearly covers the run

Expected cost per episode: ~22.5 credits (clip) + ~2 credits (thumbnail) = ~24.5 credits.
Current balance (as of setup): 3,000.35 credits (~4 months of runway at 30 episodes/month).

## Known platform limitations

- **TikTok caption in `DRAFT` mode**: TikTok's inbox-init API does not accept
  `post_info`, so `tiktok_caption` can't be attached to draft/inbox uploads — this is a
  TikTok API limitation, not a bug. The caption appears in the Actions job summary for
  manual copy/paste when finishing the post in the TikTok app. Once `TIKTOK_POST_MODE`
  is `SELF_ONLY`/`PUBLIC_TO_EVERYONE` (requires TikTok Content Posting API approval),
  the caption + a video-frame cover are set automatically.
- **YouTube custom thumbnails**: require the channel to be phone-verified
  ("Feature eligibility"). If not verified, `thumbnails().set()` errors but the video
  upload still succeeds.

## Daily automation

For fully unattended daily runs: set up a Claude Code scheduled trigger
(claude.ai/code → repo → scheduled triggers) running `/coffee-cats-malak-daily` once
per day. Each run generates the episode and fires `workflow_dispatch` itself, which
triggers Tier 2 posting automatically.

## Infrastructure notes

- `storyowl-autopost.yml` and `storyowl-merge-and-post.yml` are content-agnostic
  and reused as-is — no changes needed.
- No Cloudinary upload required for single-clip episodes — pass the Higgsfield
  CloudFront URL directly to `storyowl-autopost.yml`.
- If a future episode needs two clips merged, use `storyowl-merge-and-post.yml` with
  `clip1_url` + `clip2_url` (ffmpeg concat on GitHub Actions runners).
