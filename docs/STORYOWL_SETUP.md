# StoryOwl Auto-Post: Setup Guide

This sets up the Tier 2 pipeline (`.github/workflows/storyowl-autopost.yml`) that
auto-posts finished episodes to YouTube and TikTok, replacing the n8n "StoryOwl
Auto-Poster" workflow.

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
**fully public daily posting** (see "Daily Automation" below), `TIKTOK_POST_MODE` must
be `PUBLIC_TO_EVERYONE`, which requires TikTok to approve the app's Content Posting API
audit for Direct Post.

## 4. Optional repo variables

- `INCLUDE_VIDEO_IN_ARTIFACT` = `true` to attach the downloaded video to the workflow's
  build artifact (useful for debugging; off by default to save storage).

## 5. YouTube thumbnails

`/storyowl-daily` generates a thumbnail (Higgsfield `nano_banana_2`), uploads it to
Cloudinary as `storyowl_ep<X>_thumb`, and passes its URL as `thumbnail_url` in the
`repository_dispatch` payload. The orchestrator downloads it and calls
`youtube.thumbnails().set(...)` after the video upload succeeds.

**Requirement**: setting a custom video thumbnail requires the YouTube channel to be
**verified** (Settings > Channel > Feature eligibility > phone verification). If the
channel isn't verified, `thumbnails().set` returns an error - the video still uploads
successfully, but the job summary will show "thumbnail not set" with the error detail.
Verify the channel once and re-run; no code changes needed.

## 6. Updating StoryOwl's trigger (replacing the n8n webhook)

StoryOwl currently POSTs `{video_url, title, description}` to an n8n webhook. Point it
at GitHub's `repository_dispatch` API instead:

**Before (n8n):**
```python
requests.post("https://your-n8n.app/webhook/storyowl", json={
    "video_url": video_url, "title": title, "description": description,
})
```

**After (GitHub `repository_dispatch`):**
```python
import requests

requests.post(
    "https://api.github.com/repos/<owner>/<repo>/dispatches",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_PAT}",
        "X-GitHub-Api-Version": "2022-11-28",
    },
    json={
        "event_type": "storyowl_video_ready",
        "client_payload": {
            "video_url": video_url,
            "thumbnail_url": thumbnail_url,
            "youtube_title": youtube_title,
            "youtube_description": youtube_description,
            "youtube_tags": "tag1, tag2, tag3",
            "tiktok_caption": tiktok_caption,
        },
    },
)
```

`GITHUB_PAT` needs `repo` scope (classic PAT) or fine-grained access to this repo with
**Contents: read-only** + **Actions: read and write**.

If you're using the `/storyowl-daily` skill (`docs/STORYOWL_RUNBOOK.md`), this call is
made for you as the final step of generating an episode.

## 7. Daily automation at 9am

The Tier 2 posting pipeline (this workflow) only runs once it's handed a finished
video - it can't generate episodes by itself, because Tier 1 generation (script,
Higgsfield clips/voiceover/thumbnail, Cloudinary merge) happens via MCP tools inside an
agent session and can't run on a bare GitHub Actions cron.

To run the whole pipeline automatically every day:

1. In the Claude Code web UI (claude.ai/code), open this repo and go to its
   **scheduled triggers / routines** settings.
2. Create a daily schedule for **9:00 AM** (your local timezone) that runs the
   `/storyowl-daily` prompt against the `claude/youtube-tiktok-automation-kpyxe0` (or
   `main`, once merged) branch.
3. Each run will: pick the next entry from `docs/StoryOwl_60_Day_Plan.md`, generate the
   episode, write the YouTube/TikTok metadata, and fire `repository_dispatch` - which
   triggers this workflow to post automatically. No manual step needed once this is set
   up.

**For both platforms to post fully publicly** with no manual steps:
- **YouTube**: already posts as a public, Made-for-Kids Short by default - nothing
  further to configure.
- **TikTok**: set `TIKTOK_POST_MODE` = `PUBLIC_TO_EVERYONE` (see section 3) once
  TikTok's Content Posting API audit is approved. Until then, `DRAFT` mode still runs
  daily, but each episode lands in the TikTok inbox for you to tap "Post" (with the
  caption pasted from the job summary).

## 8. Testing

Before wiring up the real trigger, test the pipeline manually:

1. Go to the repo's **Actions** tab > **StoryOwl Auto-Post** > **Run workflow**.
2. Fill in `video_url` with any public `.mp4` URL, plus sample title/description/caption.
3. Run it. With no secrets configured yet, it runs in **dry-run mode**: downloads the
   video and shows the generated YouTube/TikTok metadata in the run's summary - no
   actual posting happens, and the run won't fail.
4. Once secrets are configured, re-run with a real episode's Cloudinary URL and confirm
   it appears on YouTube (public, Made-for-Kids Short) and TikTok (per
   `TIKTOK_POST_MODE`).

## Troubleshooting

- **YouTube quota**: `videos.insert` costs 1600 of the default 10,000 daily quota units
  (~6 uploads/day). Request a quota increase if StoryOwl needs to post more often.
- **TikTok token errors**: access tokens last ~24h; `tiktok_uploader.py` refreshes one
  automatically from `TIKTOK_REFRESH_TOKEN` on every run. If refresh fails, re-run
  `tiktok_oauth.py` to mint a new refresh token.
- **YouTube refresh token stopped working after a week**: the OAuth consent screen is
  probably still in "Testing" - switch it to "Production" and re-run `youtube_oauth.py`.
