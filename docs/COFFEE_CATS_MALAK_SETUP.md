# Coffee, Cats & Malak — Setup Guide

This sets up the posting pipeline for the Coffee, Cats & Malak channel.
The pipeline reuses StoryOwl's GitHub Actions infrastructure — same workflows,
same scripts, same secrets. If StoryOwl secrets are already configured, skip to
Section 4 (channel rebrand).

---

## 1. YouTube (Data API v3)

1. In [Google Cloud Console](https://console.cloud.google.com/), create/select a
   project and enable **YouTube Data API v3**.
2. Go to **APIs & Services > OAuth consent screen**:
   - Set publishing status to **Production** (not "Testing"). Testing tokens expire
     after 7 days and will silently break the daily pipeline.
3. Go to **APIs & Services > Credentials > Create Credentials > OAuth client ID**:
   - Application type: **Desktop app**. Download the client JSON.
4. Run the local auth helper (from your own machine):
   ```bash
   pip install -r scripts/storyowl/local_auth/requirements-local.txt
   python scripts/storyowl/local_auth/youtube_oauth.py --client-secrets path/to/client_secret.json
   ```
5. Add the three printed values as **GitHub repo secrets**:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`

---

## 2. TikTok (Content Posting API)

1. Create an app at [developers.tiktok.com](https://developers.tiktok.com/) and add
   the **Content Posting API** product.
2. Register a redirect URI on the app (e.g. `https://localhost/callback`).
3. Run the local auth helper:
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

---

## 3. TikTok Posting Mode

Set a **repo variable** (Settings > Secrets and variables > Actions > Variables):

- `TIKTOK_POST_MODE` = `DRAFT` (recommended to start)

| Value | Behavior | Caption | Requirement |
|---|---|---|---|
| `DRAFT` | Uploads to TikTok inbox; you tap "Post" in app | Manual (copy from Actions summary) | None — works immediately |
| `SELF_ONLY` | Direct Post, visible only to you | Auto-set | Content Posting API access |
| `PUBLIC_TO_EVERYONE` | Fully public Direct Post | Auto-set | Approved Content Posting API audit |

---

## 4. Channel Rebrand (manual — do this in the apps)

These cannot be changed via API — must be done manually:

**YouTube Studio** (studio.youtube.com):
- Channel name: `Coffee, Cats & Malak`
- Handle: `@CoffeeCatsMalak` (or similar)
- Bio: `One girl, three cats, zero peace and quiet ☕😹 New episode every day.`
- Profile photo: upload the animated group portrait (Malak + 3 cats, Pixar style)
- Banner: optional — use a still from any episode

**TikTok App**:
- Username / display name: `Coffee, Cats & Malak`
- Bio: `One girl, three cats, zero peace and quiet ☕😹`
- Profile photo: same animated group portrait

---

## 5. Higgsfield Character Reference Elements

After running the one-time setup session, update `docs/COFFEE_CATS_MALAK_RUNBOOK.md`
with the four element IDs:

| Character | Element ID |
|---|---|
| Malak | (paste here after creation) |
| Mocha | (paste here after creation) |
| Sky | (paste here after creation) |
| Olive | (paste here after creation) |

These IDs are embedded in every daily clip prompt to keep characters visually consistent.

---

## 6. Daily Automation (2 episodes/day)

In claude.ai/code → repo → scheduled triggers, create **two** triggers:

1. **Morning trigger** — prompt: `/coffee-cats-malak-daily`, schedule: daily at
   9:00 AM (your local timezone), branch: `main`
2. **Evening trigger** — prompt: `/coffee-cats-malak-daily`, schedule: daily at
   6:00 PM, branch: `main`

Each run picks the next episode not marked Done (the calendar is ordered
Day 1 AM, Day 1 PM, Day 2 AM, …) → generates clip + thumbnail → posts to YouTube
and TikTok → marks the episode Done. No manual step needed.

---

## 7. Testing Before Going Live

1. Go to Actions tab → **StoryOwl Auto-Post** → **Run workflow**
2. Fill in `video_url` with any public `.mp4` URL + sample title/description/caption
3. Run it — with no secrets configured it runs in dry-run mode (no actual posting)
4. Once secrets are set, run with a real Higgsfield URL and confirm it appears on
   YouTube (public Short) and TikTok (per `TIKTOK_POST_MODE`)

---

## Troubleshooting

- **YouTube refresh token stopped working after a week**: OAuth consent is still in
  "Testing" — switch to "Production" and re-run `youtube_oauth.py`
- **TikTok token errors**: `tiktok_uploader.py` auto-refreshes on every run; if it
  fails, re-run `tiktok_oauth.py` to mint a new refresh token
- **YouTube thumbnails not setting**: channel must be phone-verified in YouTube Studio
  (Settings > Channel > Feature eligibility). Video still posts without thumbnail.
