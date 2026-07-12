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
- Check the calendar row's **Energy** column — it sets the pacing:
  - **Chaotic** episodes: pack the 15 seconds with physical comedy in 3 beats —
    1. **Setup (0–3s)**: calm moment from the Setup column
    2. **Escalation (3–11s)**: the cat does the annoying thing REPEATEDLY and
       increasingly — multiple jumps, repeated pawing, knocking things one after
       another, zoomies. Never a single action; always 2–4 escalating actions.
    3. **Payoff (11–15s)**: Malak's BIG exaggerated reaction — bolts upright,
       messy hair over her face, wide cartoon eyes, dramatic slump, silent scream
       at the camera. Pixar-level exaggerated expression is the punchline.
  - **Cozy** episodes: slow warm pacing, soft moments, gentle purring cuddles —
    but still end with one small surprise or subtle comedic beat.
- Write ACTION VERBS: pounces, springs, bolts, knocks, scrambles, launches,
  freezes, whips around. Avoid static verbs like "sits" or "looks" for chaotic beats.
- Describe exaggerated reactions physically: "hair sticking up in all directions",
  "eyes comically wide", "deadpan slow blink", "dramatic collapse onto the couch".
- **MANDATORY style block** — every clip prompt MUST end with this exact sentence
  (this is the Episode 1 look; it is the channel's locked visual identity):
  > `Fully stylized Pixar/Disney 3D cartoon animation with cartoon proportions, big
  > expressive animated eyes, soft rounded features, NOT photorealistic, no live-action
  > look, no realistic human skin — animated movie style. Warm cozy apartment, soft
  > golden lighting.`
  Never shorten it to just "Pixar/CGI animated style" — that phrasing alone drifts
  toward photorealistic humans (this happened in Episode 2). The full block above is
  what keeps Malak looking like a cartoon character.
- Never include dialogue, subtitles, or on-screen text
- Keep it visual — expressions, body language, cat behavior carry the comedy

**Example prompt (Chaotic):**
> `<<<MALAK_ID>>> <<<OLIVE_ID>>> Malak is sleeping peacefully in her cozy bedroom at
> dawn. Olive the tabby cat pounces onto the bed, paws at Malak's hand, gets no
> response, then jumps on her head — once, twice, bouncing insistently. Malak bolts
> upright in shock, dark wavy hair a wild mess covering her face, eyes comically wide,
> while Olive sits beside her calmly grooming a paw as if nothing happened. Exaggerated
> physical comedy, dynamic motion. Fully stylized Pixar/Disney 3D cartoon animation
> with cartoon proportions, big expressive animated eyes, soft rounded features, NOT
> photorealistic, no live-action look, no realistic human skin — animated movie style.
> Warm cozy apartment, soft golden lighting.`

**Example prompt (Cozy):**
> `<<<MALAK_ID>>> <<<SKY_ID>>> Evening, warm lamplight. Malak reads on the couch under
> a blanket. Sky the white kitten climbs slowly into her lap, circles twice, and curls
> up purring. Malak smiles softly — then Sky stretches and gently boops Malak's chin
> with one paw. Fully stylized Pixar/Disney 3D cartoon animation with cartoon
> proportions, big expressive animated eyes, soft rounded features, NOT photorealistic,
> no live-action look, no realistic human skin — animated movie style. Warm cozy
> apartment, soft golden lighting.`

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
- End with the same mandatory style block as the clip prompt: "Fully stylized
  Pixar/Disney 3D cartoon animation with cartoon proportions, big expressive animated
  eyes, soft rounded features, NOT photorealistic, no live-action look — animated
  movie style. Bright vibrant colors, expressive faces."
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
