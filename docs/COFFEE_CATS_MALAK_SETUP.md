# Coffee, Cats & Malak Auto-Post: Setup Guide

This sets up the Tier 2 pipeline (`.github/workflows/storyowl-autopost.yml` /
`storyowl-merge-and-post.yml`) that auto-posts finished clips to YouTube and TikTok.
Same accounts and credentials as the channel's earlier "StoryOwl" era — only the
content format and branding changed, not the OAuth setup below.

## 1. YouTube (Data API v3)

1. In [Google Cloud Console](https://console.cloud.google.com/), create/select a
   project and enable **YouTube Data API v3**.
2. Go to **APIs & Services > OAuth consent screen**:
   - Set the publishing status to **Production** (not "Testing"). This is important -
     refresh tokens for apps in "Testing" expire after 7 days, which would silently
     break the pipeline weekly.
3. Go to **APIs & Services > Credentials > Create Credentials > OAuth client ID**:
   - Application type: **Desktop app**.
   - Download the client JSON.
4. Run the local helper (from your own machine, not CI):
   ```bash
   pip install -r scripts/storyowl/local_auth/requirements-local.txt
   python scripts/storyowl/local_auth/youtube_oauth.py --client-secrets path/to/client_secret.json
   ```
   Follow the printed instructions (open a URL, approve access, paste the redirect URL
   back). This works from any device - no desktop browser popup required, unlike n8n's
   "Sign in with Google".
5. Add the three printed values as **GitHub repo secrets** (Settings > Secrets and
   variables > Actions > Secrets):
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`

## 2. TikTok (Content Posting API)

1. Create an app at [developers.tiktok.com](https://developers.tiktok.com/) and add the
   **Content Posting API** product.
2. Register a redirect URI on the app (any value works, e.g. `https://localhost/callback`
   - it doesn't need to resolve).
3. Run the local helper:
   ```bash
   python scripts/storyowl/local_auth/tiktok_oauth.py \
     --client-key YOUR_CLIENT_KEY \
     --client-secret YOUR_CLIENT_SECRET \
     --redirect-uri https://localhost/callback
   ```
4. Add the printed values as **GitHub repo secrets**:
   - `TIKTOK_CLIENT_KEY`
   - `TIKTOK_CLIENT_SECRET`
   - `TIKTOK_REFRESH_TOKEN`

## 3. TikTok posting mode

Set a **repo variable** (Settings > Secrets and variables > Actions > Variables):

- `TIKTOK_POST_MODE` = `DRAFT` (default/recommended to start)

This controls how `scripts/storyowl/tiktok_uploader.py` posts:

| Value | Behavior | Caption & cover | Requirement |
|---|---|---|---|
| `DRAFT` | Uploads to the creator's TikTok inbox; you tap "Post" in the app | Not set by the API (TikTok limitation) - copy the generated caption from the Actions job summary | None - works immediately |
| `SELF_ONLY` | Direct Post, but private (visible only to you) | Set automatically | Content Posting API access |
| `PUBLIC_TO_EVERYONE` | Direct Post, fully public | Set automatically | Approved Content Posting API access for Direct Post |

As TikTok's review progresses, just change this variable - no code changes needed. For
**fully public daily posting** (see "Daily automation" below), `TIKTOK_POST_MODE` must
be `PUBLIC_TO_EVERYONE`, which requires TikTok to approve the app's Content Posting API
audit for Direct Post.

## 4. Optional repo variables

- `INCLUDE_VIDEO_IN_ARTIFACT` = `true` to attach the downloaded video to the workflow's
  build artifact (useful for debugging; off by default to save storage).

## 5. YouTube thumbnails

`/coffee-cats-malak-daily` generates a thumbnail (Higgsfield `nano_banana_2`) and
passes its URL directly as `thumbnail_url` (Higgsfield URL for single-clip posts, or
alongside the merge workflow's clip inputs for two-clip posts). The orchestrator
downloads it and calls `youtube.thumbnails().set(...)` after the video upload succeeds.

**Requirement**: setting a custom video thumbnail requires the YouTube channel to be
**verified** (Settings > Channel > Feature eligibility > phone verification). If the
channel isn't verified, `thumbnails().set` returns an error - the video still uploads
successfully, but the job summary will show "thumbnail not set" with the error detail.
Verify the channel once and re-run; no code changes needed.

## 6. Account rebrand (manual — not automatable)

Neither the YouTube Data API nor TikTok's Content Posting API expose profile/identity
editing to this pipeline, so the following are **manual, one-time steps** in each
platform's own app/dashboard — not something any script here can do:

- Rename the channel/account to **Coffee, Cats & Malak**.
- Update the bio to: *"One girl, three cats, zero peace and quiet ☕😹"*
- Upload the new profile photo (generate a portrait crop of Malak's character element
  via Higgsfield once credits allow, then upload it yourself).

## 7. Daily automation

To run the whole pipeline automatically every day:

1. In the Claude Code web UI (claude.ai/code), open this repo and go to its
   **scheduled triggers / routines** settings.
2. Create a daily schedule that runs the `/coffee-cats-malak-daily` prompt against
   the working branch (or `main`, once merged).
3. Each run will: pick the next entry from `docs/CoffeeCatsMalak_Content_Calendar.md`,
   generate the clip(s), write the YouTube/TikTok metadata, and trigger the posting
   workflow directly via the GitHub MCP connector - no manual step needed once this is
   set up.

**For both platforms to post fully publicly** with no manual steps:
- **YouTube**: already posts as a public Short by default - nothing further to
  configure.
- **TikTok**: set `TIKTOK_POST_MODE` = `PUBLIC_TO_EVERYONE` (see section 3) once
  TikTok's Content Posting API audit is approved. Until then, `DRAFT` mode still runs
  daily, but each clip lands in the TikTok inbox for you to tap "Post" (with the
  caption pasted from the job summary).

## 8. Testing

Before wiring up the real trigger, test the pipeline manually:

1. Go to the repo's **Actions** tab > **Coffee, Cats & Malak Auto-Post** (or
   **Merge and Post**) > **Run workflow**.
2. Fill in `video_url` (or `clip1_url`/`clip2_url` for the merge workflow) with any
   public `.mp4` URL, plus sample title/description/caption.
3. Run it. With no secrets configured yet, it runs in **dry-run mode**: downloads the
   video and shows the generated YouTube/TikTok metadata in the run's summary - no
   actual posting happens, and the run won't fail.
4. Once secrets are configured, re-run with a real clip's URL and confirm it appears on
   YouTube (public Short) and TikTok (per `TIKTOK_POST_MODE`).

## Troubleshooting

- **YouTube quota**: `videos.insert` costs 1600 of the default 10,000 daily quota units
  (~6 uploads/day). Request a quota increase if the channel needs to post more often.
- **TikTok token errors**: access tokens last ~24h; `tiktok_uploader.py` refreshes one
  automatically from `TIKTOK_REFRESH_TOKEN` on every run. If refresh fails, re-run
  `tiktok_oauth.py` to mint a new refresh token.
- **YouTube refresh token stopped working after a week**: the OAuth consent screen is
  probably still in "Testing" - switch it to "Production" and re-run `youtube_oauth.py`.
- **Higgsfield credits**: character-element creation and every clip/thumbnail
  generation draws from the Higgsfield credit balance - check it before a run if
  generation fails unexpectedly.
