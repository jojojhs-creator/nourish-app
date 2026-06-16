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

**First**: confirm the exact episode to produce by reading the `docs/StoryOwl_60_Day_Plan.md`
table row for this day — use the Title and Premise/Moral from that row verbatim. Do NOT
invent a different story.

Write a clip-by-clip script for the 1-minute episode (4 × 15s clips):

- **Clip 1** — StoryOwl opens a glowing storybook by candlelight, visibly talking
  (intro / hook for the day's story).
- **Clips 2-3** — the story itself, with brand-new characters for this episode.
- **Clip 4** — StoryOwl delivers the closing and closes the book.

> **Owl naming rule**: The host character is always called **"StoryOwl"** (or simply
> "the owl") in the script and voiceover. The reference element description may contain
> the name "Cleo" — ignore it. Never use "Cleo" in the script or narration.

**Adapt Clip 4's closing by content type** (check the "Type" column in the plan):

| Type | Clip 4 closing |
|---|---|
| Bedtime | StoryOwl shares the moral, says goodnight, blows out the candle |
| Fable | StoryOwl states the moral and asks viewers: "What would *you* have done?" |
| Educational | StoryOwl restates the fact and invites viewers to share it with a friend |
| Adventure | StoryOwl cheers the hero's triumph and teases "what happens next time" |
| Funny | StoryOwl laughs, wraps up, and invites viewers to share with someone who needs a smile |
| Folklore | StoryOwl closes the ancient book and says "this story has been told for a thousand years — now you're part of it" |

If the episode is **Arabic**, write the full script **with tashkeel (diacritics)** -
the "Nour" TTS voice mispronounces undiacritized Arabic.

### 2. Generate the 4 video clips (Higgsfield)

Use `generate_video` with these exact params for **every clip**:
- `model: "video_standard"` (Seedance 2.0)
- `params.mode: "fast"`
- `params.resolution: "480p"`
- `params.aspect_ratio: "9:16"` (Shorts/TikTok portrait)
- `params.duration: 15` ← **required — do not omit; default is 4 s which gives a 16 s video**

Per-clip rules:
- **Clips 1 & 4**: embed `<<<e5996a7c-1d8d-4531-9172-5eee2c844404>>>` in the prompt so
  the StoryOwl character stays visually consistent. Do **not** mention "Cleo" in the prompt.
- **Clips 2-3**: new characters per episode, matching the script's scene descriptions.

### 3. Generate the voiceover (Higgsfield inworld TTS)

Use `generate_audio` with:
- **English episodes**: voice "Olivia"
- **Arabic episodes**: voice "Nour" (script must already have full diacritics)

One voiceover track for the full ~60-second narration.

### 4. Generate the thumbnail (Higgsfield nano_banana_2)

Use `generate_image` (nano_banana_2 model) to create the episode thumbnail.

### 5. Upload assets to Cloudinary

Upload all 6 files via the Cloudinary MCP `upload-asset` tool with consistent names:

- `storyowl_ep<X>_clip1`, `storyowl_ep<X>_clip2`, `storyowl_ep<X>_clip3`, `storyowl_ep<X>_clip4`
- `storyowl_ep<X>_voice`
- `storyowl_ep<X>_thumb` (the nano_banana_2 thumbnail from step 4) - its Cloudinary URL
  becomes `thumbnail_url` in step 8

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
- `youtube_tags` - comma-separated topical tags suited to the content type — e.g.
  `#BedtimeStory #KidsStories #Shorts` for bedtime, `#FableForKids #MoralStory` for
  fables, `#LearnWithStoryOwl #KidsFacts` for educational, `#KidsAdventure` for adventure
- `tiktok_caption` - hook + inline hashtags, ≤2200 chars

> **TikTok caption note**: TikTok's "send to inbox" API (used in `DRAFT` mode) doesn't
> accept a caption - this is a TikTok platform limitation. The `tiktok_caption` written
> here is still generated, included in the auto-post job summary, and applied
> automatically once `TIKTOK_POST_MODE` is `SELF_ONLY` or `PUBLIC_TO_EVERYONE`. In
> `DRAFT` mode, copy it from the job summary when finishing the post in the TikTok app.

### 8. Trigger auto-posting

Use the **GitHub MCP `actions_run_trigger` tool** to dispatch the posting workflow
directly — no `GITHUB_PAT` environment variable needed, since the GitHub connector in
the session is already authenticated:

```
mcp__github__actions_run_trigger:
  method: run_workflow
  owner: jojojhs-creator
  repo: nourish-app
  workflow_id: storyowl-autopost.yml
  ref: main
  inputs:
    video_url: <cloudinary mp4 url>
    thumbnail_url: <cloudinary thumbnail image url>
    youtube_title: <title>
    youtube_description: <description>
    youtube_tags: <tag1, tag2, tag3>
    tiktok_caption: <caption with hashtags>
```

This triggers `.github/workflows/storyowl-autopost.yml` via `workflow_dispatch`, which
downloads the video and posts it to YouTube and TikTok automatically (see
`docs/STORYOWL_SETUP.md` for the one-time credential setup, and `TIKTOK_POST_MODE` for
current TikTok posting behavior).

### 9. Update progress

Mark the day's entry as done in `docs/StoryOwl_60_Day_Plan.md` so the next
`/storyowl-daily` run picks up the following day.
