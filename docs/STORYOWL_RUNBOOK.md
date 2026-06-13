# StoryOwl Episode Runbook ("StoryOwl day X")

This is the precise, repeatable procedure an agent session follows to produce one
StoryOwl episode and hand it off to the auto-posting pipeline
(`.github/workflows/storyowl-autopost.yml`). It's wrapped as the
`/storyowl-daily` skill (see `.claude/skills/storyowl-daily/SKILL.md`), but can also be
run manually step by step.

## Inputs

- The next unfinished entry in `docs/StoryOwl_60_Day_Plan.md` (day number, language,
  title/premise, moral).
- Episode number `X` for asset naming (`storyowl_epX_*`).

## Steps

### 1. Write the episode script

Write a clip-by-clip script for the 1-minute episode (4 × 15s clips):

- **Clip 1** — StoryOwl opens a glowing storybook by candlelight, visibly talking
  (intro / hook for the day's story).
- **Clips 2-3** — the story itself, with brand-new characters for this episode.
- **Clip 4** — StoryOwl shares the moral, says goodnight, blows out the candle.

If the episode is **Arabic**, write the full script **with tashkeel (diacritics)** -
the "Nour" TTS voice mispronounces undiacritized Arabic.

### 2. Generate the 4 video clips (Higgsfield)

Use `generate_video` (Seedance 2.0 FAST, 9:16, 480p) for each clip:

- Clips 1 & 4: include the saved **"StoryOwl" reference element** (look it up via
  `show_reference_elements` / `show_characters`) so the owl stays visually consistent.
- Clips 2-3: new characters per episode, matching the script's scene descriptions.

### 3. Generate the voiceover (Higgsfield inworld TTS)

Use `generate_audio` with:
- **English episodes**: voice "Olivia"
- **Arabic episodes**: voice "Nour" (script must already have full diacritics)

One voiceover track for the full ~60-second narration.

### 4. Generate the thumbnail (Higgsfield nano_banana_2)

Use `generate_image` (nano_banana_2 model) to create the episode thumbnail.

### 5. Upload assets to Cloudinary

Upload all 5 files via the Cloudinary MCP `upload-asset` tool with consistent names:

- `storyowl_ep<X>_clip1`, `storyowl_ep<X>_clip2`, `storyowl_ep<X>_clip3`, `storyowl_ep<X>_clip4`
- `storyowl_ep<X>_voice`

### 6. Merge into the final video (Cloudinary)

Run a single Cloudinary `transform-asset` command that:
- Strips the original audio from all 4 clips
- Splices the 4 clips together in order (one continuous ~60s video)
- Overlays the voiceover as the only audio track

The result is one finished MP4 URL - this is `video_url` for the next step.

### 7. Write platform metadata

Write, for this episode:

- `youtube_title` - catchy, ≤100 chars
- `youtube_description` - a few sentences about the story + moral, include `#Shorts`
- `youtube_tags` - comma-separated topical tags (the orchestrator also adds curated
  bedtime-story hashtags as a fallback, but episode-specific tags from here are better)
- `tiktok_caption` - hook + inline hashtags, ≤2200 chars

### 8. Trigger auto-posting

POST to GitHub's `repository_dispatch` API to hand off to Tier 2:

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/<owner>/<repo>/dispatches \
  -d '{
    "event_type": "storyowl_video_ready",
    "client_payload": {
      "video_url": "<cloudinary mp4 url>",
      "youtube_title": "<title>",
      "youtube_description": "<description>",
      "youtube_tags": "<tag1, tag2, tag3>",
      "tiktok_caption": "<caption with hashtags>"
    }
  }'
```

This triggers `.github/workflows/storyowl-autopost.yml`, which downloads the video and
posts it to YouTube and TikTok automatically (see `docs/STORYOWL_SETUP.md` for the
one-time credential setup, and `TIKTOK_POST_MODE` for current TikTok posting behavior).

### 9. Update progress

Mark the day's entry as done in `docs/StoryOwl_60_Day_Plan.md` so the next
`/storyowl-daily` run picks up the following day.
