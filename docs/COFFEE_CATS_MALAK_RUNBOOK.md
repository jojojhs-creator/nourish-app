# Coffee, Cats & Malak — Episode Runbook

Precise, repeatable procedure for producing one episode and handing it off to the
auto-posting pipeline. Wrapped as the `/coffee-cats-malak-daily` skill but can be
run manually step by step.

---

## Character Reference Element IDs

Embed these in every clip prompt using `<<<element_id>>>` syntax.
Only include characters who appear in the scenario.

| Character | Element ID | Notes |
|---|---|---|
| Malak | `1a65de6a-8d89-45e6-853f-383fb1e0ed6e` | Brunette, dark wavy hair, brown eyes, olive skin |
| Mocha | `f35a2c1b-9058-46d9-ac48-a44628d95785` | Golden Scottish Fold, folded ears, yellow-green eyes |
| Sky | `5df3dade-6a3a-4622-898c-a26e164f56f6` | White fluffy kitten, blue eyes |
| Olive | `74a58910-181f-4819-a00f-73f076bf5d69` | Classic tabby, striped, sleepy expression |

---

## Step 0 — Credit Check (mandatory before every run)

```
1. Call balance → log current credits
2. Call generate_video(get_cost: true, model: "seedance_2_0", duration: 15) → log cost
3. Call generate_image(get_cost: true, model: "nano_banana_pro") → log cost
4. Confirm total cost fits within balance before proceeding
```

Expected: ~22.5 credits for clip + ~2 credits for thumbnail = ~24.5 credits per episode.

---

## Step 1 — Pick the Scenario

Read `docs/CoffeeCatsMalak_Content_Calendar.md`.
Find the next row where Status = "Not started".
Note: Day number, Title, Characters, Setup, Payoff.

---

## Step 2 — Generate the 15s Clip

Use `generate_video` with these exact params:

```
model: "seedance_2_0"
params:
  mode: "fast"
  resolution: "480p"
  aspect_ratio: "9:16"
  duration: 15
  prompt: <see prompt guidelines below>
  # DO NOT include generate_audio — omit it entirely
```

### Prompt guidelines

- Open with the character element IDs for all characters in the scene:
  `<<<MALAK_ID>>> <<<MOCHA_ID>>>` etc.
- Describe the scene setup from the calendar row (Setup column)
- Describe the payoff / punchline (Payoff column)
- Always specify: "Pixar/CGI animated style, warm cozy apartment, soft lighting"
- Never include dialogue, subtitles, or on-screen text
- Keep it visual — focus on expressions, body language, cat behavior

**Example prompt:**
> `<<<MALAK_ID>>> <<<OLIVE_ID>>> Malak is working at her laptop on the couch in a cozy
> apartment. Olive the tabby cat silently walks over, sniffs the keyboard, then sits
> directly on top of it and stares at Malak. Malak looks at the camera in exasperation.
> Pixar/CGI animated style, warm golden lighting, cozy living room.`

### After generation

Call `job_display` with the job ID to confirm completion and get the CloudFront URL.
Save the URL as `clip_url`.

---

## Step 3 — Generate the Thumbnail

Use `generate_image` with:

```
model: "nano_banana_pro"
params:
  aspect_ratio: "9:16"
  prompt: <scene highlight, see guidelines below>
```

### Thumbnail prompt guidelines

- Show the funniest or most visually striking moment from the scenario
- Include `<<<MALAK_ID>>>` if Malak is visible
- Include relevant cat element IDs
- Add: "Pixar/CGI animation style, bright vibrant colors, expressive faces"
- No text, no overlays

Save the image URL as `thumbnail_url`.

---

## Step 4 — Write Platform Metadata

### YouTube title
Short, punchy, emoji-friendly. Max 70 chars. Examples:
- "My cat judged my entire work day 😐"
- "Tried to have coffee. The cats had other plans ☕"
- "She knocked it over and walked away like nothing happened"

### YouTube description
2–3 sentences. Warm, relatable tone. End with channel tagline.
"One girl, three cats, zero peace and quiet. New episode every day ☕😹"

### YouTube tags
`cats,funny cats,cat videos,animated cats,coffee cats malak,cat shorts,
cat animation,cute cats,cozy,daily cats,shorts`

### TikTok caption
Hook + 5–8 hashtags. Max 150 chars. Examples:
- "The audacity 😭 #catsoftiktok #catlife #funnycats #shorts #animation #fyp #viral"
- "Every. Single. Morning. ☕ #coffeecatsmalak #cats #catlover #funnyanimals #fyp"

---

## Step 5 — Trigger Posting

Use `mcp__github__actions_run_trigger`:

```
method: run_workflow
owner: jojojhs-creator
repo: nourish-app
workflow_id: storyowl-autopost.yml
ref: main
inputs:
  video_url: <clip_url>
  thumbnail_url: <thumbnail_url>
  youtube_title: <title>
  youtube_description: <description>
  youtube_tags: <tags>
  tiktok_caption: <caption>
```

No Cloudinary upload needed — pass the Higgsfield CloudFront URL directly.

---

## Step 6 — Mark Done

In `docs/CoffeeCatsMalak_Content_Calendar.md`, update the episode row:
- Status: `Done`
- Add the Higgsfield clip URL in the Notes column

---

## Troubleshooting

- **Out of credits**: check balance, do not proceed, notify user
- **Generation fails**: retry once; if it fails again, skip to next scenario and note the failure
- **Workflow dispatch fails**: check GitHub MCP connection; retry up to 3 times
- **TikTok DRAFT mode**: caption cannot be set via API — it appears in the Actions job
  summary for manual copy/paste in the TikTok app
