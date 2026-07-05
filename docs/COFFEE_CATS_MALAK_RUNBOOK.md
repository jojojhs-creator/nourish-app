# Coffee, Cats & Malak Runbook ("Coffee Cats Malak day X")

This is the precise, repeatable procedure an agent session follows to produce one
Coffee, Cats & Malak daily-life clip and hand it off to the auto-posting pipeline. It's
wrapped as the `/coffee-cats-malak-daily` skill
(see `.claude/skills/coffee-cats-malak-daily/SKILL.md`), but can also be run manually
step by step.

## Inputs

- The next unfinished entry in `docs/CoffeeCatsMalak_Content_Calendar.md` (day number,
  scene type, cast, premise).

## Character reference elements

Built once via Higgsfield's reference-element feature (`show_reference_elements`,
`action: create`) from real photos, then reused in every clip by embedding
`<<<element_id>>>` in the generation prompt. **Fill in each ID below once created** —
do not generate a scenario clip for a character whose element ID is still blank.

| Character | Description | Element ID |
|---|---|---|
| Malak | Real person (consent given for animated likeness). Brunette, tall. Cozy loungewear, apartment kitchen setting, warm morning light, city-skyline window. | _(not yet created)_ |
| Olive | Bengal/Tabby mix. Bold, mischievous. | _(not yet created)_ |
| Mocha | Golden Chinchilla Scottish Fold. Fluffy, cozy, dramatic napper. | _(not yet created)_ |
| Sky | White Persian, heterochromia (one blue eye, one green/gold eye). Diva-ish. | _(not yet created)_ |

> **Naming rule**: always use "Malak", "Olive", "Mocha", "Sky" by name in prompts/
> metadata — never a placeholder or generic description once the element exists.

## Steps

### 1. Write the scene

**First**: confirm the exact scenario by reading the
`docs/CoffeeCatsMalak_Content_Calendar.md` row for this day — use the cast and premise
from that row verbatim. Do NOT invent a different scenario.

Decide **single-clip (15s)** vs. **two-clip (30s)** based on the scenario:
- Single clip: one continuous beat (e.g. "Sky asleep in a sunbeam all afternoon").
- Two clips: a scene with a clear before/after or setup/payoff (e.g. clip 1 = Olive
  licking Malak's face to wake her, clip 2 = Malak sitting up in a panic while Olive
  looks smug).

Style for every clip: semi-realistic 3D/CGI (Pixar-adjacent), warm natural lighting,
cozy apartment interior, occasional city-skyline window shots. No dialogue. No
on-screen text/captions. Audio is ambient/silent with only light non-verbal reactions
(a sigh, an annoyed groan, a cat chirp/meow) baked in by Seedance — describe the
reaction in the prompt, don't write spoken lines.

### 2. Generate the clip(s) (Higgsfield)

Use `generate_video` with these params for **every clip**:
- `model: "video_standard"` (Seedance 2.0)
- `params.mode: "fast"`
- `params.resolution: "480p"`
- `params.aspect_ratio: "9:16"`
- `params.duration: 15` ← required — do not omit
- Do **not** set `generate_audio` at all (omit it) — Seedance bakes in matching
  ambient sound/music, same rule as the channel's hype clips.

Embed the relevant character element ID(s) from the table above in the prompt for any
character appearing in the shot — e.g. `<<<malak_element_id>>> waking up startled as
<<<olive_element_id>>> jumps on her pillow`. Never invent a placeholder ID; if an
element hasn't been created yet, stop and say so instead of generating without it.

For two-clip scenes, clip 1 and clip 2 must show distinct, sequential beats of the
same scene — never repeat a clip. If one clip fails to generate, wait and retry rather
than reusing the other clip in its place.

### 3. Generate the thumbnail (Higgsfield nano_banana_2)

Use `generate_image` (nano_banana_2 model) for a 9:16 thumbnail capturing the scene's
key beat, using the same character element IDs for consistency.

### 4. Post

**Single-clip (15s) scenarios** — no Cloudinary, no merge step. Trigger
`storyowl-autopost.yml` directly with the Higgsfield clip URL:

```
mcp__github__actions_run_trigger:
  method: run_workflow
  owner: jojojhs-creator
  repo: nourish-app
  workflow_id: storyowl-autopost.yml
  ref: main
  inputs:
    video_url: <higgsfield clip URL>
    thumbnail_url: <higgsfield thumbnail URL>
    youtube_title: <title>
    youtube_description: <description>
    youtube_tags: <tag1, tag2, tag3>
    tiktok_caption: <caption with hashtags>
```

**Two-clip (30s) scenarios** — trigger `storyowl-merge-and-post.yml`, which
ffmpeg-concatenates the two clips (keeping each clip's own baked-in audio). Leave
`clip3_url`, `clip4_url`, and `voice_url` empty — this format has no voiceover track:

```
mcp__github__actions_run_trigger:
  method: run_workflow
  owner: jojojhs-creator
  repo: nourish-app
  workflow_id: storyowl-merge-and-post.yml
  ref: main
  inputs:
    clip1_url: <higgsfield clip 1 URL>
    clip2_url: <higgsfield clip 2 URL>
    thumbnail_url: <higgsfield thumbnail URL>
    youtube_title: <title>
    youtube_description: <description>
    youtube_tags: <tag1, tag2, tag3>
    tiktok_caption: <caption with hashtags>
```

### 5. Write platform metadata

Write, for this post:

- `youtube_title` - catchy, ≤100 chars
- `youtube_description` - a sentence or two about the scene, include `#Shorts`
- `youtube_tags` - comma-separated topical tags, e.g. `#CatsOfYouTube #ApartmentLife
  #CozyVibes #Shorts`
- `tiktok_caption` - hook + inline hashtags, ≤2200 chars. This is normal platform post
  metadata (not an on-screen overlay) — still written even though the video itself has
  no burned-in captions.

> **TikTok caption note**: TikTok's "send to inbox" API (used in `DRAFT` mode) doesn't
> accept a caption - this is a TikTok platform limitation. The `tiktok_caption` written
> here is still generated, included in the auto-post job summary, and applied
> automatically once `TIKTOK_POST_MODE` is `SELF_ONLY` or `PUBLIC_TO_EVERYONE`. In
> `DRAFT` mode, copy it from the job summary when finishing the post in the TikTok app.

### 6. Update progress

Mark the day's entry as done in `docs/CoffeeCatsMalak_Content_Calendar.md` so the next
`/coffee-cats-malak-daily` run picks up the following day.
